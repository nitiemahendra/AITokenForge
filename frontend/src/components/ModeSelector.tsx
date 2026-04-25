import React, { useState } from 'react';
import clsx from 'clsx';
import { Plus, Trash2, ChevronDown } from 'lucide-react';
import type { OptimizationMode } from '../types';
import type { CustomModel } from '../hooks/useCustomModels';
import { CustomModelDialog } from './CustomModelDialog';

interface ModeSelectorProps {
  mode: OptimizationMode;
  targetModel: string;
  onModeChange: (mode: OptimizationMode) => void;
  onModelChange: (model: string) => void;
  models: Array<{ id: string; name: string; provider: string }>;
  customModels: CustomModel[];
  onAddCustomModel: (m: Omit<CustomModel, 'id' | 'createdAt'>) => void;
  onRemoveCustomModel: (id: string) => void;
}

const MODES: Array<{
  value: OptimizationMode;
  label: string;
  tagline: string;
  icon: string;
  ring: string;
  active: string;
}> = [
  {
    value: 'safe',
    label: 'Safe',
    tagline: 'Gentle touch',
    icon: '🛡️',
    ring: 'ring-emerald-500/60',
    active: 'bg-emerald-500/10 border-emerald-500/50 text-emerald-300',
  },
  {
    value: 'balanced',
    label: 'Balanced',
    tagline: 'Best of both',
    icon: '⚖️',
    ring: 'ring-sky-500/60',
    active: 'bg-sky-500/10 border-sky-500/50 text-sky-300',
  },
  {
    value: 'aggressive',
    label: 'Aggressive',
    tagline: 'Maximum cut',
    icon: '⚡',
    ring: 'ring-orange-500/60',
    active: 'bg-orange-500/10 border-orange-500/50 text-orange-300',
  },
];

const PROVIDER_GROUPS: Record<string, string> = {
  openai: 'OpenAI',
  anthropic: 'Anthropic',
  google: 'Google',
  custom: 'Other',
};

export const ModeSelector: React.FC<ModeSelectorProps> = ({
  mode,
  targetModel,
  onModeChange,
  onModelChange,
  models,
  customModels,
  onAddCustomModel,
  onRemoveCustomModel,
}) => {
  const [showDialog, setShowDialog] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const allModels = [
    ...models.filter((m) => m.id !== 'custom'),
    ...customModels.map((c) => ({ id: c.id, name: c.name, provider: c.provider.toLowerCase() })),
  ];

  const selected = allModels.find((m) => m.id === targetModel);
  const selectedLabel = selected?.name ?? 'Select model';

  const grouped = allModels.reduce<Record<string, typeof allModels>>(
    (acc, m) => {
      const group = PROVIDER_GROUPS[m.provider] ?? m.provider;
      if (!acc[group]) acc[group] = [];
      acc[group].push(m);
      return acc;
    },
    {}
  );

  const isCustom = (id: string) => customModels.some((c) => c.id === id);

  return (
    <>
      {showDialog && (
        <CustomModelDialog
          onAdd={(m) => { onAddCustomModel(m); }}
          onClose={() => setShowDialog(false)}
        />
      )}

      <div className="space-y-5">
        {/* Mode picker */}
        <div>
          <p className="text-[11px] font-semibold text-gray-500 uppercase tracking-widest mb-2.5">
            Optimization mode
          </p>
          <div className="grid grid-cols-3 gap-2">
            {MODES.map((m) => (
              <button
                key={m.value}
                onClick={() => onModeChange(m.value)}
                className={clsx(
                  'relative flex flex-col items-start p-3.5 rounded-xl border transition-all duration-150 text-left',
                  mode === m.value
                    ? `${m.active} ring-1 ${m.ring}`
                    : 'border-[#1e2028] text-gray-500 hover:border-[#2a2d3a] hover:text-gray-400 bg-[#0d0f14]'
                )}
              >
                <span className="text-xl mb-1.5">{m.icon}</span>
                <span className="font-semibold text-sm leading-tight">{m.label}</span>
                <span className="text-[11px] opacity-60 mt-0.5">{m.tagline}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Model picker */}
        <div>
          <p className="text-[11px] font-semibold text-gray-500 uppercase tracking-widest mb-2.5">
            Target model
            <span className="normal-case font-normal text-gray-600 ml-1 tracking-normal">— for cost estimation</span>
          </p>
          <div className="relative">
            <button
              onClick={() => setDropdownOpen((v) => !v)}
              className="w-full flex items-center justify-between bg-[#0d0f14] border border-[#2a2d3a] hover:border-[#3a3d4a] text-gray-200 rounded-xl px-3.5 py-2.5 text-sm transition-colors"
            >
              <span className="truncate">{selectedLabel}</span>
              <ChevronDown className={clsx('w-4 h-4 text-gray-500 shrink-0 ml-2 transition-transform', dropdownOpen && 'rotate-180')} />
            </button>

            {dropdownOpen && (
              <div className="absolute z-40 w-full mt-1.5 bg-[#13151c] border border-[#2a2d3a] rounded-xl shadow-xl overflow-hidden">
                <div className="max-h-64 overflow-y-auto py-1">
                  {Object.entries(grouped).map(([group, mods]) => (
                    <div key={group}>
                      <div className="px-3 pt-2.5 pb-1">
                        <span className="text-[10px] font-semibold text-gray-600 uppercase tracking-widest">{group}</span>
                      </div>
                      {mods.map((m) => (
                        <div
                          key={m.id}
                          className={clsx(
                            'flex items-center justify-between px-3 py-2 cursor-pointer transition-colors group',
                            targetModel === m.id
                              ? 'bg-violet-500/15 text-violet-300'
                              : 'text-gray-300 hover:bg-[#1a1d26]'
                          )}
                          onClick={() => { onModelChange(m.id); setDropdownOpen(false); }}
                        >
                          <span className="text-sm">{m.name}</span>
                          {isCustom(m.id) && (
                            <button
                              onClick={(e) => { e.stopPropagation(); onRemoveCustomModel(m.id); }}
                              className="opacity-0 group-hover:opacity-100 text-gray-600 hover:text-red-400 transition-all p-0.5 rounded"
                            >
                              <Trash2 className="w-3 h-3" />
                            </button>
                          )}
                        </div>
                      ))}
                    </div>
                  ))}
                </div>

                {/* Add custom model */}
                <div className="border-t border-[#1e2028] p-1.5">
                  <button
                    onClick={() => { setDropdownOpen(false); setShowDialog(true); }}
                    className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-400 hover:text-violet-300 hover:bg-violet-500/10 transition-colors"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    Add custom model…
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
};
