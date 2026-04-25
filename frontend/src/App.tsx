import { useState, useCallback, useRef } from 'react';
import { Zap, Github, FileText } from 'lucide-react';
import { PromptInput } from './components/PromptInput';
import { OptimizedOutput } from './components/OptimizedOutput';
import { ModeSelector } from './components/ModeSelector';
import { ResultsPanel } from './components/ResultsPanel';
import { StatusBar } from './components/StatusBar';
import { ErrorLog } from './components/ErrorLog';
import type { LogEntry } from './components/ErrorLog';
import { useOptimize } from './hooks/useOptimize';
import { useModels } from './hooks/useModels';
import { useCustomModels } from './hooks/useCustomModels';
import type { OptimizationMode } from './types';

export default function App() {
  const [prompt, setPrompt] = useState('');
  const [mode, setMode] = useState<OptimizationMode>('balanced');
  const [targetModel, setTargetModel] = useState('gpt-4o');
  const [preserveFormatting, setPreserveFormatting] = useState(true);
  const [preserveConstraints, setPreserveConstraints] = useState(true);
  const [logEntries, setLogEntries] = useState<LogEntry[]>([]);

  const addLog = useCallback((message: string, type: LogEntry['type'] = 'error') => {
    setLogEntries((prev) => [
      ...prev,
      { id: `${Date.now()}-${Math.random()}`, timestamp: new Date(), message, type },
    ]);
  }, []);

  const { result, analysis, loading, analyzing, error, optimize, analyze, reset } = useOptimize();
  const { models } = useModels();
  const { customModels, addModel, removeModel, computeCost } = useCustomModels();

  const analyzeTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handlePromptChange = useCallback((v: string) => {
    setPrompt(v);
    if (analyzeTimer.current) clearTimeout(analyzeTimer.current);
    analyzeTimer.current = setTimeout(() => {
      if (v.trim().length > 10) analyze(v, 'gpt-4o');
    }, 700);
  }, [analyze]);

  const handleOptimize = useCallback(() => {
    if (!prompt.trim() || loading) return;
    const isCustom = customModels.some((c) => c.id === targetModel);
    optimize({
      prompt,
      mode,
      target_model: isCustom ? 'custom' : (targetModel as never),
      preserve_formatting: preserveFormatting,
      preserve_constraints: preserveConstraints,
    }).catch((err: unknown) => {
      addLog(err instanceof Error ? err.message : 'Optimization failed', 'error');
    });
  }, [prompt, mode, targetModel, preserveFormatting, preserveConstraints, loading, optimize, customModels, addLog]);

  const handleReset = useCallback(() => {
    setPrompt('');
    reset();
  }, [reset]);

  // Build custom cost override if user selected a custom model
  const customCostOverride = (() => {
    if (!result) return null;
    const cm = customModels.find((c) => c.id === targetModel);
    if (!cm) return null;
    // estimate output tokens same way backend does (~60% of input)
    const estOutput = Math.round(result.optimized_tokens * 0.6);
    const estOutputOrig = Math.round(result.original_tokens * 0.6);
    const before = computeCost(cm.id, result.original_tokens, estOutputOrig) ?? 0;
    const after  = computeCost(cm.id, result.optimized_tokens, estOutput) ?? 0;
    return { before, after, modelName: cm.name };
  })();

  return (
    <div className="min-h-screen bg-[#080a0f] text-gray-100" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>

      {/* ── Header ─────────────────────────────────────────────────────── */}
      <header className="sticky top-0 z-20 bg-[#080a0f]/90 backdrop-blur-md border-b border-[#1e2028]">
        <div className="max-w-6xl mx-auto px-5 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="bg-sky-600 p-1.5 rounded-lg">
                <Zap className="w-4 h-4 text-white" />
              </div>
              <div className="absolute -bottom-0.5 -right-0.5 w-2 h-2 bg-emerald-500 rounded-full border border-[#080a0f]" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="font-bold text-white text-[15px] tracking-tight">TokenForge</span>
              <span className="text-[11px] text-gray-600 hidden sm:inline">AI Cost Optimization</span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <StatusBar onLog={addLog} />
            <div className="flex items-center gap-1 text-gray-700">
              <a href="https://github.com" target="_blank" rel="noreferrer"
                className="p-1.5 rounded-lg hover:bg-[#1a1d26] hover:text-gray-400 transition-colors">
                <Github className="w-4 h-4" />
              </a>
              <a href="/docs" className="p-1.5 rounded-lg hover:bg-[#1a1d26] hover:text-gray-400 transition-colors">
                <FileText className="w-4 h-4" />
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* ── Main ───────────────────────────────────────────────────────── */}
      <main className="max-w-6xl mx-auto px-5 py-6">
        <div className="grid grid-cols-1 xl:grid-cols-[300px_1fr] gap-5">

          {/* ── Left sidebar: controls ── */}
          <div className="space-y-4">
            <div className="bg-[#0d0f14] border border-[#1e2028] rounded-2xl p-4">
              <ModeSelector
                mode={mode}
                targetModel={targetModel}
                onModeChange={setMode}
                onModelChange={setTargetModel}
                models={models}
                customModels={customModels}
                onAddCustomModel={addModel}
                onRemoveCustomModel={removeModel}
              />

              {/* Options */}
              <div className="mt-4 pt-4 border-t border-[#1e2028] space-y-2.5">
                <p className="text-[11px] font-semibold text-gray-500 uppercase tracking-widest">Constraints</p>
                {[
                  { label: 'Keep formatting', sub: 'markdown, code blocks', checked: preserveFormatting, set: setPreserveFormatting },
                  { label: 'Keep constraints', sub: 'rules and requirements', checked: preserveConstraints, set: setPreserveConstraints },
                ].map(({ label, sub, checked, set }) => (
                  <label key={label} className="flex items-start gap-3 cursor-pointer group">
                    <div className="relative mt-0.5">
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={(e) => set(e.target.checked)}
                        className="sr-only"
                      />
                      <div className={`w-4 h-4 rounded border transition-colors ${
                        checked ? 'bg-sky-600 border-sky-600' : 'border-[#3a3d4a] bg-[#0d0f14]'
                      }`}>
                        {checked && (
                          <svg className="w-3 h-3 text-white absolute inset-0.5" fill="none" viewBox="0 0 12 12">
                            <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                          </svg>
                        )}
                      </div>
                    </div>
                    <div>
                      <p className="text-xs text-gray-300 group-hover:text-gray-200 transition-colors">{label}</p>
                      <p className="text-[10px] text-gray-600">{sub}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Live analysis card */}
            {analysis && !result && (
              <div className="bg-[#0d0f14] border border-[#1e2028] rounded-2xl p-4">
                <p className="text-[11px] font-semibold text-gray-500 uppercase tracking-widest mb-3">Live count</p>
                <div className="space-y-2 text-xs">
                  {[
                    { label: 'Input tokens', value: analysis.token_analysis.token_count.toLocaleString(), color: 'text-sky-400' },
                    { label: 'Est. output', value: analysis.token_analysis.estimated_output_tokens.toLocaleString(), color: 'text-gray-400' },
                    { label: 'Est. cost', value: `$${analysis.cost_estimate.total_cost.toFixed(5)}`, color: 'text-gray-400' },
                  ].map(({ label, value, color }) => (
                    <div key={label} className="flex justify-between">
                      <span className="text-gray-600">{label}</span>
                      <span className={`font-mono font-semibold ${color}`}>{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* ── Right: editor + results ── */}
          <div className="space-y-4">
            {/* Prompt panels */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-[#0d0f14] border border-[#1e2028] rounded-2xl p-4">
                <PromptInput
                  value={prompt}
                  onChange={handlePromptChange}
                  onOptimize={handleOptimize}
                  onReset={handleReset}
                  loading={loading}
                  tokenCount={analysis?.token_analysis.token_count}
                  analyzing={analyzing}
                />
              </div>
              <div className="bg-[#0d0f14] border border-[#1e2028] rounded-2xl p-4">
                <OptimizedOutput result={result} loading={loading} />
              </div>
            </div>

            {/* Inline error banner (also pushed to log) */}
            {error && (
              <div className="bg-red-500/8 border border-red-500/25 rounded-xl p-4">
                <p className="text-sm font-semibold text-red-400 mb-1">Optimization failed</p>
                <p className="text-xs text-red-400/70">{error}</p>
                <p className="text-xs text-gray-600 mt-2">
                  Make sure Ollama is running:{' '}
                  <code className="font-mono bg-[#1a1d26] px-1.5 py-0.5 rounded text-gray-400">ollama serve</code>
                </p>
              </div>
            )}

            {/* Results panel */}
            {result && <ResultsPanel result={result} customCost={customCostOverride} />}

            {/* Empty state */}
            {!result && !loading && !error && (
              <div className="border border-dashed border-[#1e2028] rounded-2xl p-8 text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-[#0d0f14] border border-[#1e2028] mb-3">
                  <Zap className="w-5 h-5 text-gray-700" />
                </div>
                <p className="text-sm text-gray-600 font-medium">Run an optimization to see results</p>
                <p className="text-xs text-gray-700 mt-1">Token savings · cost estimates · semantic score</p>
              </div>
            )}

            {/* Error log */}
            <ErrorLog
              entries={logEntries}
              onClear={() => setLogEntries([])}
            />
          </div>
        </div>
      </main>

      {/* ── Footer ── */}
      <footer className="border-t border-[#1e2028] mt-8 py-4">
        <div className="max-w-6xl mx-auto px-5 flex items-center justify-between text-[11px] text-gray-700">
          <span>TokenForge — local-first AI cost optimization</span>
          <span>All processing happens on your machine</span>
        </div>
      </footer>
    </div>
  );
}
