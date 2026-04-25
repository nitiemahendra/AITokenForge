export type OptimizationMode = 'safe' | 'balanced' | 'aggressive';

export type TargetModel =
  // OpenAI
  | 'gpt-5'
  | 'gpt-4.1'
  | 'gpt-4.1-mini'
  | 'gpt-4.1-nano'
  | 'o3'
  | 'o4-mini'
  | 'gpt-4o'
  | 'gpt-4o-mini'
  // Anthropic
  | 'claude-opus-4-7'
  | 'claude-opus-4-5'
  | 'claude-sonnet-4-5'
  | 'claude-sonnet-4-6'
  | 'claude-haiku-4-5'
  // Google
  | 'gemini-3-pro'
  | 'gemini-2.5-pro'
  | 'gemini-2.5-flash'
  | 'gemini-2.0-flash'
  // xAI
  | 'grok-3'
  | 'grok-3-mini'
  // DeepSeek
  | 'deepseek-v3'
  | 'deepseek-r1'
  // Meta
  | 'llama-4-maverick'
  | 'llama-4-scout'
  // Alibaba
  | 'qwen3-235b'
  | 'qwen3-30b'
  // Moonshot
  | 'kimi-k2'
  | 'custom';

export interface OptimizeRequest {
  prompt: string;
  mode: OptimizationMode;
  target_model: TargetModel;
  preserve_formatting?: boolean;
  preserve_constraints?: boolean;
  max_compression_ratio?: number | null;
  context?: string | null;
}

export interface AnalyzeRequest {
  prompt: string;
  target_model: TargetModel;
  include_breakdown?: boolean;
}

export interface TokenBreakdown {
  segment: string;
  token_count: number;
  type: string;
}

export interface TokenAnalysis {
  token_count: number;
  estimated_output_tokens: number;
  total_estimated_tokens: number;
  tokenizer_used: string;
  breakdown?: TokenBreakdown[] | null;
}

export interface CostEstimate {
  input_cost: number;
  estimated_output_cost: number;
  total_cost: number;
  currency: string;
  model: string;
  pricing_per_1k_input: number;
  pricing_per_1k_output: number;
}

export interface OptimizeResponse {
  request_id: string;
  original_prompt: string;
  optimized_prompt: string;
  original_tokens: number;
  optimized_tokens: number;
  token_reduction_percent: number;
  semantic_similarity: number;
  risk_level: 'low' | 'medium' | 'high';
  estimated_cost_before: number;
  estimated_cost_after: number;
  cost_savings_percent: number;
  optimization_mode: string;
  target_model: string;
  processing_time_ms: number;
  llm_adapter_used: string;
  warnings: string[];
  metadata: Record<string, unknown>;
}

export interface AnalyzeResponse {
  request_id: string;
  prompt: string;
  token_analysis: TokenAnalysis;
  cost_estimate: CostEstimate;
  processing_time_ms: number;
  metadata: Record<string, unknown>;
}

export interface ModelInfo {
  id: string;
  name: string;
  provider: string;
  context_window: number;
  pricing_input_per_1k: number;
  pricing_output_per_1k: number;
  supports_optimization: boolean;
}

export interface ModelsResponse {
  models: ModelInfo[];
  llm_adapters: string[];
  optimization_modes: string[];
}

export interface HealthResponse {
  status: string;
  version: string;
  llm_adapter: string;
  llm_available: boolean;
  embedding_model: string;
  embedding_available: boolean;
  uptime_seconds: number;
  models_loaded: string[];
}
