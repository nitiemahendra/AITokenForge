import axios from 'axios';
import type {
  OptimizeRequest,
  OptimizeResponse,
  AnalyzeRequest,
  AnalyzeResponse,
  ModelsResponse,
  HealthResponse,
} from '../types';

const BASE_URL = (import.meta as { env?: { VITE_API_URL?: string } }).env?.VITE_API_URL ?? '';

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 180_000, // 3 min for slow local LLM
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const message =
      err.response?.data?.detail ?? err.message ?? 'Unknown error';
    return Promise.reject(new Error(message));
  }
);

export const apiClient = {
  optimize: (req: OptimizeRequest): Promise<OptimizeResponse> =>
    api.post<OptimizeResponse>('/api/v1/optimize', req).then((r) => r.data),

  analyze: (req: AnalyzeRequest): Promise<AnalyzeResponse> =>
    api.post<AnalyzeResponse>('/api/v1/analyze', req).then((r) => r.data),

  getModels: (): Promise<ModelsResponse> =>
    api.get<ModelsResponse>('/models').then((r) => r.data),

  getHealth: (): Promise<HealthResponse> =>
    api.get<HealthResponse>('/health').then((r) => r.data),

  restartServer: (): Promise<{ status: string; message: string }> =>
    api.post('/api/v1/admin/restart').then((r) => r.data),
};
