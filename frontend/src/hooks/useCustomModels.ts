import { useState, useCallback } from 'react';

export interface CustomModel {
  id: string;
  name: string;
  provider: string;
  inputPer1k: number;
  outputPer1k: number;
  contextWindow: number;
  createdAt: number;
}

const STORAGE_KEY = 'tokenforge_custom_models';

function load(): CustomModel[] {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '[]');
  } catch {
    return [];
  }
}

function save(models: CustomModel[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(models));
}

export function useCustomModels() {
  const [customModels, setCustomModels] = useState<CustomModel[]>(load);

  const addModel = useCallback((m: Omit<CustomModel, 'id' | 'createdAt'>) => {
    const model: CustomModel = {
      ...m,
      id: `custom_${Date.now()}`,
      createdAt: Date.now(),
    };
    setCustomModels((prev) => {
      const next = [...prev, model];
      save(next);
      return next;
    });
    return model;
  }, []);

  const removeModel = useCallback((id: string) => {
    setCustomModels((prev) => {
      const next = prev.filter((m) => m.id !== id);
      save(next);
      return next;
    });
  }, []);

  const computeCost = useCallback(
    (modelId: string, inputTokens: number, outputTokens: number): number | null => {
      const m = customModels.find((c) => c.id === modelId);
      if (!m) return null;
      return (inputTokens / 1000) * m.inputPer1k + (outputTokens / 1000) * m.outputPer1k;
    },
    [customModels]
  );

  return { customModels, addModel, removeModel, computeCost };
}
