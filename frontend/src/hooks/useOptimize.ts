import { useState, useCallback } from 'react';
import { apiClient } from '../api/client';
import type { OptimizeRequest, OptimizeResponse, AnalyzeResponse } from '../types';

interface UseOptimizeReturn {
  result: OptimizeResponse | null;
  analysis: AnalyzeResponse | null;
  loading: boolean;
  analyzing: boolean;
  error: string | null;
  optimize: (req: OptimizeRequest) => Promise<void>;
  analyze: (prompt: string, targetModel: string) => Promise<void>;
  reset: () => void;
}

export function useOptimize(): UseOptimizeReturn {
  const [result, setResult] = useState<OptimizeResponse | null>(null);
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const optimize = useCallback(async (req: OptimizeRequest) => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.optimize(req);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Optimization failed');
    } finally {
      setLoading(false);
    }
  }, []);

  const analyze = useCallback(async (prompt: string, targetModel: string) => {
    if (!prompt.trim()) return;
    setAnalyzing(true);
    try {
      const res = await apiClient.analyze({
        prompt,
        target_model: targetModel as never,
        include_breakdown: false,
      });
      setAnalysis(res);
    } catch {
      // Analysis errors are silent — not blocking
    } finally {
      setAnalyzing(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setAnalysis(null);
    setError(null);
  }, []);

  return { result, analysis, loading, analyzing, error, optimize, analyze, reset };
}
