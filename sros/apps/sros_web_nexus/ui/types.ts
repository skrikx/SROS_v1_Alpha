export type ModuleCategory = 'Physics' | 'Research' | 'Automation' | 'Visuals' | 'System';

export type VizType = 'GRAPH' | 'GRID' | 'TERMINAL' | 'IMAGE';

export interface ModuleConfig {
  temperature: number;
  topK: number;
  topP: number;
  maxSteps: number;
}

export interface SrosModuleDef {
  id: string;
  name: string;
  category: ModuleCategory;
  vizType: VizType;
  summary: string;
  promptProfile: string;
  defaultConfig: ModuleConfig;
  description?: string;
  icon?: string;
  status?: string;
}

export interface SimulationDataPoint {
  t: number;
  v1: number;
  v2: number;
}

export interface SimulationResponse {
  logs: string[];
  data: SimulationDataPoint[];
}

// --- Prime Agent Types ---

export type AgentMode = 'STANDARD' | 'SOVEREIGN' | 'VEO' | 'HOLO' | 'LIVE';

export interface AgentMessage {
  id: string;
  role: 'user' | 'model' | 'system';
  content: string;
  timestamp: number;
  type: 'TEXT' | 'IMAGE' | 'VIDEO' | 'AUDIO' | 'TOOL_OUTPUT';
  mediaUrl?: string; // For images/videos
  metadata?: {
    thinkingTime?: number;
    groundingSources?: { title: string; uri: string }[];
    toolUsed?: string;
  };
}

export interface AgentConfig {
  imageSize: '1K' | '2K' | '4K';
  imageAspectRatio: '1:1' | '3:4' | '4:3' | '9:16' | '16:9';
  videoAspectRatio: '16:9' | '9:16';
  temperature: number;
  topK: number;
  topP: number;
  systemInstruction: string;
}

export interface AgentState {
  isThinking: boolean;
  isListening: boolean;
  isSpeaking: boolean;
  mode: AgentMode;
  grounding: {
    search: boolean;
    maps: boolean;
  };
  config: AgentConfig;
  thinkingBudget: number; // 0 to 32768
}

export interface GenericSimulationProps {
  moduleDef: SrosModuleDef;
}