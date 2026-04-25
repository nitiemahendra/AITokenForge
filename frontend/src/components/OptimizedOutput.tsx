import React, { useState } from 'react';
import { Copy, Check, AlertTriangle, Clock } from 'lucide-react';
import type { OptimizeResponse } from '../types';

interface Props {
  result: OptimizeResponse | null;
  loading: boolean;
}

export const OptimizedOutput: React.FC<Props> = ({ result, loading }) => {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    if (!result?.optimized_prompt) return;
    await navigator.clipboard.writeText(result.optimized_prompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <div className="flex flex-col h-full">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[11px] font-semibold text-gray-500 uppercase tracking-widest">Optimized prompt</span>
        </div>
        <div className="flex-1 min-h-[220px] bg-[#0d0f14] border border-[#1e2028] rounded-xl flex flex-col items-center justify-center gap-3">
          <div className="flex gap-1.5">
            {[0, 1, 2, 3].map((i) => (
              <div
                key={i}
                className="w-1.5 h-6 bg-sky-500/40 rounded-full animate-pulse"
                style={{ animationDelay: `${i * 0.15}s`, animationDuration: '1s' }}
              />
            ))}
          </div>
          <p className="text-xs text-gray-600">Local model compressing…</p>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="flex flex-col h-full">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[11px] font-semibold text-gray-500 uppercase tracking-widest">Optimized prompt</span>
        </div>
        <div className="flex-1 min-h-[220px] bg-[#0d0f14] border border-dashed border-[#1e2028] rounded-xl flex items-center justify-center p-6">
          <p className="text-sm text-gray-700 text-center leading-relaxed">
            Your compressed prompt will appear here.<br />
            <span className="text-gray-800">Tokens · cost · semantic score included.</span>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-[11px] font-semibold text-gray-500 uppercase tracking-widest">Optimized prompt</span>
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono bg-[#1a1d26] text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-full">
            {result.optimized_tokens.toLocaleString()} tokens
          </span>
          <button
            onClick={copy}
            className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-200 transition-colors px-2 py-1 rounded-lg hover:bg-[#1a1d26]"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            {copied ? 'Copied' : 'Copy'}
          </button>
        </div>
      </div>

      {/* Output area */}
      <div className="flex-1 min-h-[220px] bg-[#0d0f14] border border-[#1e2028] rounded-xl p-4 overflow-auto">
        <pre className="text-sm text-gray-200 font-mono leading-relaxed whitespace-pre-wrap break-words">
          {result.optimized_prompt}
        </pre>
      </div>

      {/* Warnings */}
      {result.warnings.length > 0 && (
        <div className="mt-2 space-y-1">
          {result.warnings.map((w, i) => (
            <div key={i} className="flex items-start gap-2 bg-amber-500/8 border border-amber-500/20 rounded-lg px-3 py-2">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-500 mt-0.5 shrink-0" />
              <p className="text-xs text-amber-400/90">{w}</p>
            </div>
          ))}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center gap-1 mt-2 text-[10px] text-gray-700">
        <Clock className="w-3 h-3" />
        <span>{result.processing_time_ms.toFixed(0)}ms</span>
        <span className="mx-1">·</span>
        <span>{result.llm_adapter_used}</span>
        <span className="mx-1">·</span>
        <span>req {result.request_id.slice(0, 8)}</span>
      </div>
    </div>
  );
};
