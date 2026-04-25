import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import type { ModelInfo } from '../types';

interface UseModelsReturn {
  models: ModelInfo[];
  optimizationModes: string[];
  loading: boolean;
  error: string | null;
}

export function useModels(): UseModelsReturn {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [optimizationModes, setOptimizationModes] = useState<string[]>(['safe', 'balanced', 'aggressive']);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiClient
      .getModels()
      .then((data) => {
        setModels(data.models);
        setOptimizationModes(data.optimization_modes);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return { models, optimizationModes, loading, error };
}
