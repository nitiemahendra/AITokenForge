import React, { useRef, useEffect, useState } from 'react';
import { ChevronDown, ChevronUp, Trash2, AlertTriangle, Info, AlertCircle } from 'lucide-react';

export interface LogEntry {
  id: string;
  timestamp: Date;
  message: string;
  type: 'error' | 'warning' | 'info';
}

interface Props {
  entries: LogEntry[];
  onClear: () => void;
}

const TYPE_STYLES = {
  error:   { label: 'ERROR',   color: 'text-red-400',   bg: 'bg-red-500/15',   icon: AlertCircle },
  warning: { label: 'WARN',    color: 'text-amber-400', bg: 'bg-amber-500/10', icon: AlertTriangle },
  info:    { label: 'INFO',    color: 'text-sky-400',   bg: 'bg-sky-500/10',   icon: Info },
};

export const ErrorLog: React.FC<Props> = ({ entries, onClear }) => {
  const [collapsed, setCollapsed] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const hasErrors = entries.some((e) => e.type === 'error');
  const errorCount = entries.filter((e) => e.type === 'error').length;

  useEffect(() => {
    if (!collapsed && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [entries.length, collapsed]);

  // Auto-expand when a new error arrives
  useEffect(() => {
    if (hasErrors) setCollapsed(false);
  }, [errorCount]);

  const borderColor = hasErrors ? 'border-red-500/25' : 'border-[#1e2028]';
  const headerBg   = hasErrors ? 'bg-red-500/5' : 'bg-[#0d0f14]';

  return (
    <div className={`border ${borderColor} rounded-xl overflow-hidden`}>
      {/* Header row */}
      <div className={`flex items-center justify-between px-4 py-2.5 ${headerBg} border-b border-[#1e2028]`}>
        <button
          onClick={() => setCollapsed((c) => !c)}
          className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-gray-500 hover:text-gray-300 transition-colors"
        >
          {collapsed
            ? <ChevronDown className="w-3.5 h-3.5" />
            : <ChevronUp   className="w-3.5 h-3.5" />}
          <span>Error Log</span>
          {entries.length > 0 && (
            <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold tabular-nums
              ${hasErrors ? 'bg-red-500/20 text-red-400' : 'bg-[#1a1d26] text-gray-500'}`}>
              {entries.length}
            </span>
          )}
        </button>

        <button
          onClick={onClear}
          className="flex items-center gap-1 text-[10px] text-gray-700 hover:text-red-400 transition-colors"
        >
          <Trash2 className="w-3 h-3" />
          Clear
        </button>
      </div>

      {/* Log body */}
      {!collapsed && (
        <div className="bg-[#080c10] max-h-52 overflow-y-auto font-mono text-[11px] leading-relaxed">
          {entries.length === 0 ? (
            <p className="text-gray-700 px-4 py-3">No messages logged.</p>
          ) : (
            <div>
              {entries.map((entry) => {
                const s = TYPE_STYLES[entry.type];
                const Icon = s.icon;
                return (
                  <div
                    key={entry.id}
                    className="flex gap-3 px-4 py-2 border-b border-[#1e2028]/50 last:border-0 hover:bg-white/[0.02] transition-colors"
                  >
                    <span className="text-gray-600 shrink-0 tabular-nums pt-px">
                      {entry.timestamp.toLocaleTimeString()}
                    </span>
                    <span className={`flex items-center gap-1 shrink-0 font-bold pt-px ${s.color}`}>
                      <Icon className="w-3 h-3" />
                      {s.label}
                    </span>
                    <span className="text-gray-400 break-all">{entry.message}</span>
                  </div>
                );
              })}
              <div ref={bottomRef} />
            </div>
          )}
        </div>
      )}
    </div>
  );
};
