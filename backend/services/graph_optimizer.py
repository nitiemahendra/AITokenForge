"""
GraphContextOptimizer — Graphify-powered structural pre-compression.

Strategy: when a prompt embeds raw file context (code blocks, doc pastes), this
service builds a Graphify knowledge graph of the referenced content and replaces
the verbose inline context with a compact entity/relationship summary.

This is a structural pass that runs BEFORE the LLM compression pass.  The two
passes are complementary:
  1. Graph pass  — collapses code/doc context  (structural, deterministic)
  2. LLM pass    — compresses prose/instructions (semantic, stochastic)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Lazy graphify import — optional dependency (pip install aitokenforge[graph])
# ---------------------------------------------------------------------------

def _graphify_available() -> bool:
    try:
        import graphify  # noqa: F401
        return True
    except ImportError:
        return False


# ---------------------------------------------------------------------------
# Heuristics for detecting inline context blocks in prompts
# ---------------------------------------------------------------------------

_CODE_FENCE_RE = re.compile(r"```[\w]*\n(.*?)```", re.DOTALL)
_FILE_BLOCK_RE = re.compile(
    r"(?:^|\n)(?:File|Path|Source):\s*([^\n]+)\n(.*?)(?=\n(?:File|Path|Source):|$)",
    re.DOTALL | re.IGNORECASE,
)


class GraphCompressionResult:
    """Carries the result of a graph pre-compression pass."""

    __slots__ = (
        "compressed_prompt",
        "nodes_extracted",
        "edges_extracted",
        "communities",
        "god_nodes",
        "tokens_before",
        "tokens_after",
        "graph_summary",
        "available",
        "skipped_reason",
    )

    def __init__(
        self,
        compressed_prompt: str,
        nodes_extracted: int = 0,
        edges_extracted: int = 0,
        communities: int = 0,
        god_nodes: list[str] | None = None,
        tokens_before: int = 0,
        tokens_after: int = 0,
        graph_summary: str = "",
        available: bool = True,
        skipped_reason: str = "",
    ):
        self.compressed_prompt = compressed_prompt
        self.nodes_extracted = nodes_extracted
        self.edges_extracted = edges_extracted
        self.communities = communities
        self.god_nodes = god_nodes or []
        self.tokens_before = tokens_before
        self.tokens_after = tokens_after
        self.graph_summary = graph_summary
        self.available = available
        self.skipped_reason = skipped_reason

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes_extracted": self.nodes_extracted,
            "edges_extracted": self.edges_extracted,
            "communities": self.communities,
            "god_nodes": self.god_nodes,
            "tokens_before": self.tokens_before,
            "tokens_after": self.tokens_after,
            "graph_summary": self.graph_summary,
            "available": self.available,
            "skipped_reason": self.skipped_reason,
        }


class GraphContextOptimizer:
    """
    Wraps Graphify to compress code/document context embedded in prompts.

    Two compression modes:
    - path mode  : given a file/directory path, build a graph and inject a
                   compact summary into the prompt instead of any raw pastes
    - inline mode: extract code fences from the prompt, parse them through
                   Graphify in-memory, replace with graph summary
    """

    def __init__(self) -> None:
        self._available = _graphify_available()
        if not self._available:
            logger.warning(
                "graphify_unavailable",
                hint="pip install aitokenforge[graph]",
            )

    @property
    def is_available(self) -> bool:
        return self._available

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compress(
        self,
        prompt: str,
        context_path: str | None = None,
        max_god_nodes: int = 10,
    ) -> GraphCompressionResult:
        """
        Run graph pre-compression on *prompt*.

        If *context_path* points to a real file/directory, analyse it and
        replace any inline raw-code context with a graph summary.

        If *context_path* is None, extract and analyse inline code fences
        from the prompt itself.
        """
        if not self._available:
            return GraphCompressionResult(
                compressed_prompt=prompt,
                available=False,
                skipped_reason="graphify not installed — pip install aitokenforge[graph]",
            )

        tokens_before = len(prompt.split())

        try:
            if context_path:
                return self._compress_from_path(prompt, Path(context_path), max_god_nodes)
            return self._compress_inline(prompt, max_god_nodes)
        except Exception as exc:
            logger.error("graph_compression_error", error=str(exc))
            return GraphCompressionResult(
                compressed_prompt=prompt,
                available=True,
                tokens_before=tokens_before,
                tokens_after=tokens_before,
                skipped_reason=f"graph analysis failed: {exc}",
            )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _compress_from_path(
        self, prompt: str, path: Path, max_god_nodes: int
    ) -> GraphCompressionResult:
        from graphify import build_from_json, cluster, extract
        from graphify.analyze import god_nodes

        tokens_before = len(prompt.split())

        if not path.exists():
            return GraphCompressionResult(
                compressed_prompt=prompt,
                available=True,
                tokens_before=tokens_before,
                tokens_after=tokens_before,
                skipped_reason=f"path not found: {path}",
            )

        logger.info("graph_extract_start", path=str(path))
        extraction = extract(path)
        G = build_from_json(extraction)
        communities = cluster(G)

        nodes = G.number_of_nodes()
        edges = G.number_of_edges()
        num_communities = len(communities)
        top_nodes = god_nodes(G, top_n=max_god_nodes)
        top_labels = [n["label"] for n in top_nodes]

        summary = _build_graph_summary(G, communities, top_nodes, path)
        compressed = _inject_graph_summary(prompt, summary)

        tokens_after = len(compressed.split())
        logger.info(
            "graph_extract_complete",
            path=str(path),
            nodes=nodes,
            edges=edges,
            communities=num_communities,
            tokens_before=tokens_before,
            tokens_after=tokens_after,
            reduction_pct=round((1 - tokens_after / max(tokens_before, 1)) * 100, 1),
        )

        return GraphCompressionResult(
            compressed_prompt=compressed,
            nodes_extracted=nodes,
            edges_extracted=edges,
            communities=num_communities,
            god_nodes=top_labels,
            tokens_before=tokens_before,
            tokens_after=tokens_after,
            graph_summary=summary,
            available=True,
        )

    def _compress_inline(self, prompt: str, max_god_nodes: int) -> GraphCompressionResult:
        """Extract code fences, analyse them, replace with graph summaries."""
        import tempfile

        from graphify import build_from_json, cluster, extract
        from graphify.analyze import god_nodes

        tokens_before = len(prompt.split())
        fences = _CODE_FENCE_RE.findall(prompt)

        if not fences:
            return GraphCompressionResult(
                compressed_prompt=prompt,
                available=True,
                tokens_before=tokens_before,
                tokens_after=tokens_before,
                skipped_reason="no inline code blocks detected",
            )

        # Write all fences to a temp directory so Graphify can analyse them
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            for i, code in enumerate(fences):
                (tmp_path / f"snippet_{i}.py").write_text(code, encoding="utf-8")

            extraction = extract(tmp_path)
            G = build_from_json(extraction)

        if G.number_of_nodes() == 0:
            return GraphCompressionResult(
                compressed_prompt=prompt,
                available=True,
                tokens_before=tokens_before,
                tokens_after=tokens_before,
                skipped_reason="no entities extracted from inline code",
            )

        communities = cluster(G)
        top_nodes = god_nodes(G, top_n=max_god_nodes)
        top_labels = [n["label"] for n in top_nodes]
        summary = _build_graph_summary(G, communities, top_nodes, path=None)

        # Replace every code fence in the prompt with a single shared summary
        compressed = _CODE_FENCE_RE.sub("", prompt).strip()
        compressed = f"{compressed}\n\n{summary}"

        tokens_after = len(compressed.split())
        return GraphCompressionResult(
            compressed_prompt=compressed,
            nodes_extracted=G.number_of_nodes(),
            edges_extracted=G.number_of_edges(),
            communities=len(communities),
            god_nodes=top_labels,
            tokens_before=tokens_before,
            tokens_after=tokens_after,
            graph_summary=summary,
            available=True,
        )


# ---------------------------------------------------------------------------
# Summary builders
# ---------------------------------------------------------------------------

def _build_graph_summary(
    G: Any,
    communities: dict,
    top_nodes: list[dict],
    path: Path | None,
) -> str:
    """
    Produce a compact, token-efficient graph summary suitable for injection
    into an LLM prompt.
    """
    source_label = f" of `{path.name}`" if path else ""
    lines: list[str] = [f"[GRAPH CONTEXT{source_label}]"]

    # Key entities (god nodes = highest centrality)
    if top_nodes:
        node_strs = []
        for n in top_nodes[:8]:
            label = n["label"]
            edges = n.get("edges", 0)
            ntype = G.nodes[n["id"]].get("type", "") if n["id"] in G.nodes else ""
            tag = f"({ntype})" if ntype else ""
            node_strs.append(f"{label}{tag}[{edges}]")
        lines.append("Key entities: " + ", ".join(node_strs))

    # Relationships (sample most connected edges)
    edge_samples: list[str] = []
    for u, v, data in G.edges(data=True):
        rel = data.get("relation", "→")
        u_label = G.nodes[u].get("label", u) if u in G.nodes else u
        v_label = G.nodes[v].get("label", v) if v in G.nodes else v
        confidence = data.get("confidence", "")
        if confidence != "AMBIGUOUS":
            edge_samples.append(f"{u_label} {rel} {v_label}")
        if len(edge_samples) >= 12:
            break
    if edge_samples:
        lines.append("Relationships: " + " | ".join(edge_samples))

    # Community summary
    if communities:
        community_sizes = sorted(
            [(cid, len(info["nodes"] if isinstance(info, dict) else info))
             for cid, info in communities.items()],
            key=lambda x: -x[1],
        )
        size_str = ", ".join(
            f"C{cid}({sz})" for cid, sz in community_sizes[:5]
        )
        lines.append(f"Communities: {size_str}")

    lines.append(
        f"Stats: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, "
        f"{len(communities)} clusters"
    )
    lines.append("[/GRAPH CONTEXT]")

    return "\n".join(lines)


def _inject_graph_summary(prompt: str, summary: str) -> str:
    """
    Replace the largest code block in the prompt with the graph summary.
    If no code block found, append the summary.
    """
    fences = list(_CODE_FENCE_RE.finditer(prompt))
    if not fences:
        return f"{prompt}\n\n{summary}"

    # Replace only the largest code block (most tokens) to avoid over-stripping
    largest = max(fences, key=lambda m: len(m.group(0)))
    return prompt[: largest.start()].rstrip() + f"\n\n{summary}\n\n" + prompt[largest.end():].lstrip()
