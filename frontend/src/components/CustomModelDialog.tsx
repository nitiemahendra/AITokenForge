import React, { useState } from 'react';
import { X, Plus, Cpu } from 'lucide-react';
import type { CustomModel } from '../hooks/useCustomModels';

interface Props {
  onAdd: (m: Omit<CustomModel, 'id' | 'createdAt'>) => void;
  onClose: () => void;
}

const PRESETS = [
  { name: 'GPT-4.1', provider: 'OpenAI', inputPer1k: 0.002, outputPer1k: 0.008, contextWindow: 1_000_000 },
  { name: 'Mistral Large', provider: 'Mistral', inputPer1k: 0.003, outputPer1k: 0.009, contextWindow: 128_000 },
  { name: 'Llama 3.3 70B', provider: 'Meta', inputPer1k: 0.00023, outputPer1k: 0.0004, contextWindow: 128_000 },
  { name: 'DeepSeek R1', provider: 'DeepSeek', inputPer1k: 0.00055, outputPer1k: 0.00219, contextWindow: 64_000 },
];

export const CustomModelDialog: React.FC<Props> = ({ onAdd, onClose }) => {
  const [name, setName] = useState('');
  const [provider, setProvider] = useState('');
  const [inputPer1k, setInputPer1k] = useState('');
  const [outputPer1k, setOutputPer1k] = useState('');
  const [contextWindow, setContextWindow] = useState('128000');
  const [error, setError] = useState('');

  const applyPreset = (p: typeof PRESETS[0]) => {
    setName(p.name);
    setProvider(p.provider);
    setInputPer1k(String(p.inputPer1k));
    setOutputPer1k(String(p.outputPer1k));
    setContextWindow(String(p.contextWindow));
    setError('');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const inp = parseFloat(inputPer1k);
    const out = parseFloat(outputPer1k);
    const ctx = parseInt(contextWindow);
    if (!name.trim()) return setError('Model name is required.');
    if (isNaN(inp) || inp < 0) return setError('Input price must be a positive number.');
    if (isNaN(out) || out < 0) return setError('Output price must be a positive number.');
    onAdd({
      name: name.trim(),
      provider: provider.trim() || 'Custom',
      inputPer1k: inp,
      outputPer1k: out,
      contextWindow: isNaN(ctx) ? 128_000 : ctx,
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="bg-[#13151c] border border-[#2a2d3a] rounded-2xl w-full max-w-md mx-4 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#1e2028]">
          <div className="flex items-center gap-2.5">
            <div className="bg-violet-500/20 p-1.5 rounded-lg">
              <Cpu className="w-4 h-4 text-violet-400" />
            </div>
            <span className="font-semibold text-white">Add Custom Model</span>
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-300 transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Presets */}
        <div className="px-6 pt-4">
          <p className="text-xs text-gray-500 mb-2">Quick presets</p>
          <div className="flex flex-wrap gap-1.5">
            {PRESETS.map((p) => (
              <button
                key={p.name}
                onClick={() => applyPreset(p)}
                className="text-xs px-2.5 py-1 rounded-full border border-[#2a2d3a] text-gray-400 hover:border-violet-500/50 hover:text-violet-300 hover:bg-violet-500/10 transition-all"
              >
                {p.name}
              </button>
            ))}
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="px-6 py-4 space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2">
              <label className="block text-xs text-gray-400 mb-1.5">Model name *</label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. My Fine-tuned Model"
                className="w-full bg-[#0d0f14] border border-[#2a2d3a] rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-violet-500/60 focus:ring-1 focus:ring-violet-500/30"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1.5">Provider</label>
              <input
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                placeholder="e.g. OpenAI"
                className="w-full bg-[#0d0f14] border border-[#2a2d3a] rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-violet-500/60 focus:ring-1 focus:ring-violet-500/30"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1.5">Context window</label>
              <input
                value={contextWindow}
                onChange={(e) => setContextWindow(e.target.value)}
                placeholder="128000"
                className="w-full bg-[#0d0f14] border border-[#2a2d3a] rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-violet-500/60 focus:ring-1 focus:ring-violet-500/30"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1.5">Input price ($ / 1K tokens)</label>
              <input
                value={inputPer1k}
                onChange={(e) => setInputPer1k(e.target.value)}
                placeholder="0.001"
                type="number"
                step="0.0001"
                min="0"
                className="w-full bg-[#0d0f14] border border-[#2a2d3a] rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-violet-500/60 focus:ring-1 focus:ring-violet-500/30"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1.5">Output price ($ / 1K tokens)</label>
              <input
                value={outputPer1k}
                onChange={(e) => setOutputPer1k(e.target.value)}
                placeholder="0.002"
                type="number"
                step="0.0001"
                min="0"
                className="w-full bg-[#0d0f14] border border-[#2a2d3a] rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-violet-500/60 focus:ring-1 focus:ring-violet-500/30"
              />
            </div>
          </div>

          {inputPer1k && outputPer1k && !isNaN(parseFloat(inputPer1k)) && (
            <div className="bg-violet-500/10 border border-violet-500/20 rounded-lg px-3 py-2 text-xs text-violet-300">
              1M tokens in · 600K tokens out ≈ ${((parseFloat(inputPer1k) * 1000) + (parseFloat(outputPer1k) * 600)).toFixed(2)} total
            </div>
          )}

          {error && <p className="text-xs text-red-400">{error}</p>}

          <div className="flex gap-2 pt-1">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2 rounded-lg border border-[#2a2d3a] text-sm text-gray-400 hover:text-gray-200 hover:border-gray-600 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              Add Model
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
