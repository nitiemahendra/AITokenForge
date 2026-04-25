import React, { useState } from 'react';
import { TrendingDown, DollarSign, ShieldCheck, ShieldAlert, Shield } from 'lucide-react';
import clsx from 'clsx';
import type { OptimizeResponse } from '../types';
import SupportBanner from './SupportBanner';

interface Props {
  result: OptimizeResponse;
  customCost?: { before: number; after: number; modelName: string } | null;
}

const fmt = (n: number) =>
  n < 0.0001 ? `$${(n * 1_000_000).toFixed(2)}µ` : n < 0.01 ? `$${(n * 1000).toFixed(3)}m` : `$${n.toFixed(4)}`;

const RISK = {
  low:    { icon: ShieldCheck, label: 'Preserved',   color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20', bar: 'bg-emerald-500' },
  medium: { icon: Shield,      label: 'Minor drift',  color: 'text-amber-400',   bg: 'bg-amber-500/10 border-amber-500/20',   bar: 'bg-amber-500' },
  high:   { icon: ShieldAlert, label: 'Review needed', color: 'text-red-400',   bg: 'bg-red-500/10 border-red-500/20',       bar: 'bg-red-500' },
};

type Tab = 'overview' | 'tokens' | 'cost' | 'semantic';

export const ResultsPanel: React.FC<Props> = ({ result, customCost }) => {
  const [tab, setTab] = useState<Tab>('overview');

  const risk = RISK[result.risk_level as keyof typeof RISK] ?? RISK.medium;
  const RiskIcon = risk.icon;

  const costBefore = customCost?.before ?? result.estimated_cost_before;
  const costAfter  = customCost?.after  ?? result.estimated_cost_after;
  const savings    = costBefore > 0 ? ((1 - costAfter / costBefore) * 100) : result.cost_savings_percent;
  const modelLabel = customCost?.modelName ?? result.target_model;
  const savedAmt   = costBefore - costAfter;

  return (
    <div className="bg-[#0d0f14] border border-[#1e2028] rounded-2xl overflow-hidden">
      {/* Tabs */}
      <div className="flex border-b border-[#1e2028]">
        {(['overview', 'tokens', 'cost', 'semantic'] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={clsx(
              'flex-1 py-2.5 text-xs font-semibold capitalize transition-colors',
              tab === t
                ? 'text-white border-b-2 border-sky-500 bg-sky-500/5'
                : 'text-gray-600 hover:text-gray-400'
            )}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="p-4">
        {/* ── Overview ── */}
        {tab === 'overview' && (
          <div className="space-y-3">
            {/* Big number */}
            <div className="text-center py-3">
              <p className="text-[11px] text-gray-600 uppercase tracking-widest mb-1">Token reduction</p>
              <p className="text-5xl font-black text-white tabular-nums">
                {result.token_reduction_percent.toFixed(1)}
                <span className="text-2xl text-sky-400 ml-1">%</span>
              </p>
              <p className="text-xs text-gray-600 mt-1">
                {result.original_tokens.toLocaleString()} → {result.optimized_tokens.toLocaleString()} tokens
              </p>
            </div>

            {/* Three stats */}
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="bg-[#13151c] rounded-xl p-3 border border-[#1e2028]">
                <TrendingDown className="w-4 h-4 text-emerald-400 mx-auto mb-1" />
                <p className="text-lg font-bold text-emerald-400">{savings.toFixed(1)}%</p>
                <p className="text-[10px] text-gray-600">cost saved</p>
              </div>
              <div className={clsx('rounded-xl p-3 border', risk.bg)}>
                <RiskIcon className={clsx('w-4 h-4 mx-auto mb-1', risk.color)} />
                <p className={clsx('text-lg font-bold', risk.color)}>
                  {(result.semantic_similarity * 100).toFixed(0)}
                </p>
                <p className="text-[10px] text-gray-600">similarity</p>
              </div>
              <div className="bg-[#13151c] rounded-xl p-3 border border-[#1e2028]">
                <DollarSign className="w-4 h-4 text-violet-400 mx-auto mb-1" />
                <p className="text-lg font-bold text-violet-400">{fmt(savedAmt)}</p>
                <p className="text-[10px] text-gray-600">per call</p>
              </div>
            </div>

            {/* Progress bar */}
            <div className="space-y-1.5 pt-1">
              <div className="flex items-center gap-2 text-xs text-gray-600">
                <span className="w-14 text-right">Original</span>
                <div className="flex-1 bg-[#1a1d26] rounded-full h-2">
                  <div className="h-2 rounded-full bg-gray-600" style={{ width: '100%' }} />
                </div>
                <span className="w-10 font-mono text-gray-500">{result.original_tokens}</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-600">
                <span className="w-14 text-right">Optimized</span>
                <div className="flex-1 bg-[#1a1d26] rounded-full h-2">
                  <div
                    className="h-2 rounded-full bg-sky-500 transition-all duration-700"
                    style={{ width: `${Math.max(4, 100 - result.token_reduction_percent)}%` }}
                  />
                </div>
                <span className="w-10 font-mono text-sky-400">{result.optimized_tokens}</span>
              </div>
            </div>
          </div>
        )}

        {/* ── Tokens ── */}
        {tab === 'tokens' && (
          <div className="space-y-3">
            <div className="flex items-end justify-between bg-[#13151c] rounded-xl p-4 border border-[#1e2028]">
              <div>
                <p className="text-[10px] text-gray-600 uppercase tracking-wider mb-1">Original</p>
                <p className="text-3xl font-black text-gray-400 tabular-nums">{result.original_tokens.toLocaleString()}</p>
              </div>
              <div className="text-center pb-1">
                <span className="text-xs text-sky-400 font-semibold">→</span>
                <p className="text-xs text-emerald-400 font-bold mt-0.5">−{result.token_reduction_percent.toFixed(1)}%</p>
              </div>
              <div className="text-right">
                <p className="text-[10px] text-gray-600 uppercase tracking-wider mb-1">Optimized</p>
                <p className="text-3xl font-black text-sky-400 tabular-nums">{result.optimized_tokens.toLocaleString()}</p>
              </div>
            </div>

            {/* Visual bar chart */}
            <div className="flex items-end gap-4 h-24 px-4 pt-2">
              {[
                { label: 'Original', value: result.original_tokens, color: 'bg-gray-600' },
                { label: 'Optimized', value: result.optimized_tokens, color: 'bg-sky-500' },
              ].map((bar) => {
                const pct = (bar.value / result.original_tokens) * 100;
                return (
                  <div key={bar.label} className="flex-1 flex flex-col items-center gap-1">
                    <span className="text-xs font-mono text-gray-500">{bar.value.toLocaleString()}</span>
                    <div className="w-full bg-[#1a1d26] rounded-t-md" style={{ height: '60px' }}>
                      <div
                        className={clsx('w-full rounded-t-md transition-all duration-700', bar.color)}
                        style={{ height: `${pct}%`, marginTop: `${100 - pct}%` }}
                      />
                    </div>
                    <span className="text-[10px] text-gray-600">{bar.label}</span>
                  </div>
                );
              })}
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="bg-[#13151c] border border-[#1e2028] rounded-lg p-2.5">
                <p className="text-gray-600 mb-0.5">Tokens removed</p>
                <p className="font-mono font-semibold text-emerald-400">
                  −{(result.original_tokens - result.optimized_tokens).toLocaleString()}
                </p>
              </div>
              <div className="bg-[#13151c] border border-[#1e2028] rounded-lg p-2.5">
                <p className="text-gray-600 mb-0.5">Compression ratio</p>
                <p className="font-mono font-semibold text-sky-400">
                  {(result.optimized_tokens / result.original_tokens).toFixed(2)}x
                </p>
              </div>
            </div>

            <p className="text-[10px] text-gray-700 text-center">
              Tokenizer: {(result.metadata?.tokenizer_used as string) ?? 'cl100k_base'} · {result.target_model}
            </p>
          </div>
        )}

        {/* ── Cost ── */}
        {tab === 'cost' && (
          <div className="space-y-3">
            {customCost && (
              <div className="bg-violet-500/10 border border-violet-500/20 rounded-lg px-3 py-2 text-xs text-violet-300">
                Using custom pricing for <strong>{customCost.modelName}</strong>
              </div>
            )}

            <div className="space-y-2">
              <div className="flex justify-between items-center p-3 bg-[#13151c] border border-[#1e2028] rounded-xl">
                <div>
                  <p className="text-xs text-gray-600">Before optimization</p>
                  <p className="text-[10px] text-gray-700 mt-0.5">{modelLabel}</p>
                </div>
                <span className="font-mono font-semibold text-gray-400">{fmt(costBefore)}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-[#13151c] border border-emerald-500/20 rounded-xl">
                <div>
                  <p className="text-xs text-emerald-400">After optimization</p>
                  <p className="text-[10px] text-gray-700 mt-0.5">{savings.toFixed(1)}% cheaper</p>
                </div>
                <span className="font-mono font-semibold text-emerald-400">{fmt(costAfter)}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-emerald-500/8 border border-emerald-500/20 rounded-xl">
                <div className="flex items-center gap-2">
                  <DollarSign className="w-4 h-4 text-emerald-400" />
                  <p className="text-sm font-semibold text-emerald-300">Savings per call</p>
                </div>
                <span className="font-mono font-bold text-emerald-400">{fmt(savedAmt)}</span>
              </div>
            </div>

            {/* Scale */}
            <div className="border-t border-[#1e2028] pt-3">
              <p className="text-[10px] text-gray-600 uppercase tracking-wider mb-2">At scale</p>
              <div className="grid grid-cols-3 gap-1.5 text-center text-xs">
                {[1_000, 100_000, 1_000_000].map((n) => (
                  <div key={n} className="bg-[#13151c] border border-[#1e2028] rounded-lg p-2">
                    <p className="text-gray-700 text-[10px]">{n >= 1_000_000 ? '1M' : n >= 100_000 ? '100K' : '1K'} calls</p>
                    <p className="font-mono text-emerald-400 font-semibold">{fmt(savedAmt * n)}</p>
                    <p className="text-gray-700 text-[9px]">saved</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ── Semantic ── */}
        {tab === 'semantic' && (
          <div className="space-y-4">
            {/* Score ring */}
            <div className="flex flex-col items-center py-2">
              <div className="relative w-28 h-28">
                <svg className="w-28 h-28 -rotate-90" viewBox="0 0 112 112">
                  <circle cx="56" cy="56" r="44" strokeWidth="8" stroke="#1a1d26" fill="none" />
                  <circle
                    cx="56" cy="56" r="44"
                    strokeWidth="8"
                    stroke="currentColor"
                    fill="none"
                    strokeLinecap="round"
                    className={risk.color}
                    strokeDasharray={`${2 * Math.PI * 44}`}
                    strokeDashoffset={`${2 * Math.PI * 44 * (1 - result.semantic_similarity)}`}
                    style={{ transition: 'stroke-dashoffset 1s ease' }}
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className={clsx('text-3xl font-black', risk.color)}>
                    {(result.semantic_similarity * 100).toFixed(0)}
                  </span>
                  <span className="text-[10px] text-gray-600">/ 100</span>
                </div>
              </div>
              <div className={clsx('mt-2 flex items-center gap-1.5 px-3 py-1 rounded-full border text-xs font-semibold', risk.bg, risk.color)}>
                <RiskIcon className="w-3.5 h-3.5" />
                {risk.label}
              </div>
            </div>

            {/* Stats */}
            <div className="space-y-2 text-xs">
              {[
                { label: 'Semantic similarity', value: result.semantic_similarity.toFixed(4), color: risk.color },
                {
                  label: 'Scoring confidence',
                  value: `${((result.metadata?.semantic_confidence as number ?? 0) * 100).toFixed(0)}%`,
                  color: 'text-gray-400',
                },
                {
                  label: 'Embedding model',
                  value: result.metadata?.embedding_model as string ?? '—',
                  color: 'text-gray-500',
                },
                { label: 'Optimization mode', value: result.optimization_mode, color: 'text-gray-500' },
              ].map(({ label, value, color }) => (
                <div key={label} className="flex justify-between items-center">
                  <span className="text-gray-600">{label}</span>
                  <span className={clsx('font-mono font-semibold', color)}>{value}</span>
                </div>
              ))}
            </div>

            {result.risk_level === 'high' && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-xs text-red-400">
                Significant semantic drift detected. Review the optimized prompt before use in production.
              </div>
            )}
          </div>
        )}
      </div>
      {result.token_reduction_percent > 20 && (
        <div className="px-4 pb-4">
          <SupportBanner savingsPercent={result.token_reduction_percent} />
        </div>
      )}
    </div>
  );
};
