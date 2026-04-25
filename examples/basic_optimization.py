"""
TokenForge Basic Usage Example
Demonstrates calling the API programmatically.
"""

import httpx
import json

BASE = "http://localhost:8000"


def optimize(prompt: str, mode: str = "balanced", model: str = "gpt-4.1") -> dict:
    r = httpx.post(f"{BASE}/api/v1/optimize", json={
        "prompt": prompt,
        "mode": mode,
        "target_model": model,
    })
    r.raise_for_status()
    return r.json()


def analyze(prompt: str, model: str = "gpt-4.1") -> dict:
    r = httpx.post(f"{BASE}/api/v1/analyze", json={
        "prompt": prompt,
        "target_model": model,
    })
    r.raise_for_status()
    return r.json()


def compare(prompt: str) -> dict:
    models = ["gpt-4.1", "claude-sonnet-4-6", "gemini-2.5-flash", "deepseek-v3"]
    results = {}
    for m in models:
        d = analyze(prompt, m)
        results[m] = {
            "cost": d["cost_estimate"]["total_cost"],
            "tokens": d["token_analysis"]["token_count"],
        }
    return dict(sorted(results.items(), key=lambda x: x[1]["cost"]))


if __name__ == "__main__":
    prompt = """
    You are a helpful AI assistant. I need you to help me with a task.
    Please provide a comprehensive and detailed explanation of what machine learning is.
    Make sure to include examples, use cases, and explain it in simple terms that
    a beginner can understand. Be thorough and cover all the important aspects.
    Don't leave anything out. This is very important for my project.
    """

    print("── Token Analysis ──────────────────────────────")
    a = analyze(prompt)
    ta, ce = a["token_analysis"], a["cost_estimate"]
    print(f"Tokens:  {ta['token_count']} input / {ta['estimated_output_tokens']} output")
    print(f"Cost:    ${ce['total_cost']:.6f} (GPT-4.1)")

    print("\n── Model Comparison ────────────────────────────")
    for model, info in compare(prompt).items():
        print(f"{model:<28} ${info['cost']:.6f}")

    print("\n── Optimization (balanced mode) ────────────────")
    result = optimize(prompt)
    print(f"Original:  {result['original_tokens']} tokens")
    print(f"Optimized: {result['optimized_tokens']} tokens")
    print(f"Reduction: {result['token_reduction_percent']:.1f}%")
    print(f"Similarity:{result['semantic_similarity']:.3f} ({result['risk_level']} risk)")
    print(f"\nOptimized prompt:\n{result['optimized_prompt']}")
