import React, { useRef, useEffect } from 'react';
import { Sparkles, X } from 'lucide-react';
import clsx from 'clsx';

interface PromptInputProps {
  value: string;
  onChange: (value: string) => void;
  onOptimize: () => void;
  onReset: () => void;
  loading: boolean;
  tokenCount?: number;
  analyzing?: boolean;
}

export const PromptInput: React.FC<PromptInputProps> = ({
  value,
  onChange,
  onOptimize,
  onReset,
  loading,
  tokenCount,
  analyzing,
}) => {
  const ref = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (ref.current) {
      ref.current.style.height = 'auto';
      ref.current.style.height = `${Math.min(ref.current.scrollHeight, 380)}px`;
    }
  }, [value]);

  const handleKey = (e: React.KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && !loading && value.trim()) {
      e.preventDefault();
      onOptimize();
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Label row */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-[11px] font-semibold text-gray-500 uppercase tracking-widest">Your prompt</span>
        <div className="flex items-center gap-2">
          {analyzing && (
            <span className="text-[11px] text-gray-600 animate-pulse">counting…</span>
          )}
          {tokenCount !== undefined && !analyzing && (
            <span className="text-xs font-mono bg-[#1a1d26] text-sky-400 border border-sky-500/20 px-2 py-0.5 rounded-full">
              {tokenCount.toLocaleString()} tokens
            </span>
          )}
          {value && (
            <button onClick={onReset} className="text-gray-600 hover:text-gray-400 transition-colors" title="Clear">
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Textarea */}
      <textarea
        ref={ref}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKey}
        disabled={loading}
        spellCheck={false}
        placeholder={"Paste a prompt to compress…\n\nWorks great with:\n• Verbose system prompts\n• Multi-step instructions\n• RAG context + questions\n• Repeated boilerplate\n\nCtrl+Enter to run"}
        className={clsx(
          'flex-1 min-h-[220px] w-full rounded-xl px-4 py-3 text-sm leading-relaxed resize-none',
          'bg-[#0d0f14] border text-gray-200 placeholder-gray-700 font-mono',
          'focus:outline-none focus:ring-1 transition-colors',
          loading
            ? 'border-[#1e2028] opacity-50 cursor-not-allowed'
            : 'border-[#1e2028] hover:border-[#2a2d3a] focus:border-sky-500/40 focus:ring-sky-500/20'
        )}
      />

      {/* Optimize button */}
      <button
        onClick={onOptimize}
        disabled={loading || !value.trim()}
        className={clsx(
          'mt-3 flex items-center justify-center gap-2 w-full py-3 rounded-xl text-sm font-semibold transition-all duration-150',
          loading || !value.trim()
            ? 'bg-[#1a1d26] text-gray-600 cursor-not-allowed'
            : 'bg-sky-600 hover:bg-sky-500 text-white shadow-lg shadow-sky-900/40 active:scale-[0.98]'
        )}
      >
        {loading ? (
          <>
            <span className="flex gap-1">
              {[0, 1, 2].map((i) => (
                <span
                  key={i}
                  className="w-1.5 h-1.5 rounded-full bg-gray-500 animate-bounce"
                  style={{ animationDelay: `${i * 0.12}s` }}
                />
              ))}
            </span>
            <span>Gemma is thinking…</span>
          </>
        ) : (
          <>
            <Sparkles className="w-4 h-4" />
            Optimize
            <kbd className="ml-1 text-[10px] opacity-50 font-normal">Ctrl+Enter</kbd>
          </>
        )}
      </button>
    </div>
  );
};
