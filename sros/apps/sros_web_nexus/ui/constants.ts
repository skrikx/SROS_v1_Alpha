import { SrosModuleDef } from './types';

export const SROS_MODULE_REGISTRY: SrosModuleDef[] = [
  // Physics
  {
    id: 'quantum-flux',
    name: 'Quantum Flux',
    category: 'Physics',
    vizType: 'GRAPH',
    summary: 'Simulates fluctuations in zero-point energy fields.',
    promptProfile: 'Generate quantum field fluctuations. v1=Field Strength, v2=Entanglement Ratio.',
    defaultConfig: { temperature: 0.7, topK: 40, topP: 0.95, maxSteps: 100 }
  },
  {
    id: 'void-oscillator',
    name: 'Void Oscillator',
    category: 'Physics',
    vizType: 'GRAPH',
    summary: 'Monitors resonant frequencies of local void pockets.',
    promptProfile: 'Simulate void resonance. v1=Frequency Hz, v2=Amplitude.',
    defaultConfig: { temperature: 0.8, topK: 40, topP: 0.95, maxSteps: 100 }
  },
  {
    id: 'aero-field',
    name: 'Aero Field',
    category: 'Physics',
    vizType: 'GRID',
    summary: 'Atmospheric density and vector analysis.',
    promptProfile: 'Simulate atmospheric turbulence. v1=Pressure, v2=Velocity.',
    defaultConfig: { temperature: 0.6, topK: 40, topP: 0.95, maxSteps: 100 }
  },
  {
    id: 'entropy-watch',
    name: 'Entropy Watch',
    category: 'Physics',
    vizType: 'GRAPH',
    summary: 'Real-time thermodynamic decay tracking.',
    promptProfile: 'Track entropy levels. v1=System Heat, v2=Order Metric.',
    defaultConfig: { temperature: 0.5, topK: 40, topP: 0.95, maxSteps: 100 }
  },
  {
    id: 'gravity-well',
    name: 'Gravity Well',
    category: 'Physics',
    vizType: 'GRAPH',
    summary: 'Gravimetric distortion sensor metrics.',
    promptProfile: 'Simulate gravity waves. v1=Micro-G, v2=Temporal Shift.',
    defaultConfig: { temperature: 0.6, topK: 40, topP: 0.95, maxSteps: 100 }
  },

  // Research
  {
    id: 'market-synth',
    name: 'Market Synth',
    category: 'Research',
    vizType: 'GRAPH',
    summary: 'Synthetic financial market projection engine.',
    promptProfile: 'Project credit values. v1=Index A, v2=Volitility.',
    defaultConfig: { temperature: 0.9, topK: 40, topP: 0.95, maxSteps: 100 }
  },
  {
    id: 'pattern-crawler',
    name: 'Pattern Crawler',
    category: 'Research',
    vizType: 'TERMINAL',
    summary: 'Deep web heuristic pattern recognition bot.',
    promptProfile: 'Scan data nodes. v1=Nodes Found, v2=Relevance Score.',
    defaultConfig: { temperature: 0.8, topK: 40, topP: 0.95, maxSteps: 100 }
  },
  {
    id: 'signal-deck',
    name: 'Signal Deck',
    category: 'Research',
    vizType: 'GRAPH',
    summary: 'RF spectrum analysis and decryption.',
    promptProfile: 'Analyze RF spectrum. v1=Signal Strength, v2=Noise Floor.',
    defaultConfig: { temperature: 0.7, topK: 40, topP: 0.95, maxSteps: 100 }
  },
  {
    id: 'hypothesis-weave',
    name: 'Hypothesis Weave',
    category: 'Research',
    vizType: 'GRID',
    summary: 'Generative scientific hypothesis threading.',
    promptProfile: 'Weave logic threads. v1=Confidence, v2=Complexity.',
    defaultConfig: { temperature: 1.0, topK: 40, topP: 0.95, maxSteps: 100 }
  },
  {
    id: 'archive-lens',
    name: 'Archive Lens',
    category: 'Research',
    vizType: 'TERMINAL',
    summary: 'Historical data restoration and analysis.',
    promptProfile: 'Restore data blocks. v1=Integrity, v2=Recovered Bytes.',
    defaultConfig: { temperature: 0.4, topK: 40, topP: 0.95, maxSteps: 100 }
  },

  // Automation
  {
    id: 'pipeline-orchestrator',
    name: 'Pipeline Orch.',
    category: 'Automation',
    vizType: 'GRAPH',
    summary: 'CI/CD and fabrication pipeline controller.',
    promptProfile: 'Manage build queue. v1=Throughput, v2=Error Rate.',
    defaultConfig: { temperature: 0.5, topK: 40, topP: 0.95, maxSteps: 100 }
  },
  {
    id: 'autoscaler',
    name: 'AutoScaler',
    category: 'Automation',
    vizType: 'GRAPH',
    summary: 'Dynamic resource allocation daemon.',
    promptProfile: 'Scale compute units. v1=CPU Load, v2=Instance Count.',
    defaultConfig: { temperature: 0.5, topK: 40, topP: 0.95, maxSteps: 100 }
  },
  {
    id: 'traffic-grid',
    name: 'Traffic Grid',
    category: 'Automation',
    vizType: 'GRID',
    summary: 'Network packet flow visualizer.',
    promptProfile: 'Route packets. v1=Inbound MBps, v2=Outbound MBps.',
    defaultConfig: { temperature: 0.6, topK: 40, topP: 0.95, maxSteps: 100 }
  },
  {
    id: 'backup-daemon',
    name: 'Backup Daemon',
    category: 'Automation',
    vizType: 'TERMINAL',
    summary: 'Redundant storage synchronization.',
    promptProfile: 'Sync storage shards. v1=Progress %, v2=Dedup Ratio.',
    defaultConfig: { temperature: 0.3, topK: 40, topP: 0.95, maxSteps: 100 }
  },
  {
    id: 'watchtower',
    name: 'Watchtower',
    category: 'Automation',
    vizType: 'TERMINAL',
    summary: 'Security perimeter intrusion detection.',
    promptProfile: 'Scan perimeter. v1=Threat Level, v2=Active Scans.',
    defaultConfig: { temperature: 0.4, topK: 40, topP: 0.95, maxSteps: 100 }
  },

  // Visuals
  {
    id: 'holo-forge',
    name: 'Holo Forge',
    category: 'Visuals',
    vizType: 'IMAGE',
    summary: 'Quantum-entangled holographic image manipulation system.',
    promptProfile: 'Edit this image.',
    defaultConfig: { temperature: 0.4, topK: 32, topP: 1, maxSteps: 1 }
  },
  {
    id: 'render-core',
    name: 'Render Core',
    category: 'Visuals',
    vizType: 'GRID',
    summary: 'High-fidelity frame rendering engine.',
    promptProfile: 'Render frames. v1=FPS, v2=Poly Count.',
    defaultConfig: { temperature: 0.6, topK: 40, topP: 0.95, maxSteps: 100 }
  },
  {
    id: 'palette-forge',
    name: 'Palette Forge',
    category: 'Visuals',
    vizType: 'GRAPH',
    summary: 'Color theory generation subsystem.',
    promptProfile: 'Mix color gamuts. v1=Saturation, v2=Harmonics.',
    defaultConfig: { temperature: 0.8, topK: 40, topP: 0.95, maxSteps: 100 }
  },
  {
    id: 'shader-loom',
    name: 'Shader Loom',
    category: 'Visuals',
    vizType: 'TERMINAL',
    summary: 'Procedural shader compilation unit.',
    promptProfile: 'Compile shaders. v1=Instructions, v2=Optimization.',
    defaultConfig: { temperature: 0.7, topK: 40, topP: 0.95, maxSteps: 100 }
  },

  // System
  {
    id: 'kernel-health',
    name: 'Kernel Health',
    category: 'System',
    vizType: 'GRAPH',
    summary: 'SROS Kernel vital signs monitor.',
    promptProfile: 'Monitor kernel. v1=Memory Usage, v2=Thread Count.',
    defaultConfig: { temperature: 0.2, topK: 40, topP: 0.95, maxSteps: 100 }
  },
  {
    id: 'mirror-report',
    name: 'Mirror Report',
    category: 'System',
    vizType: 'TERMINAL',
    summary: 'System self-diagnostic logs.',
    promptProfile: 'Run diagnostics. v1=Errors, v2=Warnings.',
    defaultConfig: { temperature: 0.2, topK: 40, topP: 0.95, maxSteps: 100 }
  },
  {
    id: 'router',
    name: 'Task Router',
    category: 'System',
    description: 'View and manage routed tasks',
    icon: 'Terminal',
    status: 'active'
  },
  {
    id: 'logs',
    name: 'System Logs',
    category: 'System',
    description: 'View system logs and traces',
    icon: 'FileText',
    status: 'active',
    vizType: 'TERMINAL',
    summary: 'View system logs and traces',
    promptProfile: 'Analyze logs',
    defaultConfig: { temperature: 0.1, topK: 1, topP: 1, maxSteps: 1 }
  },
  {
    id: 'knowledge-browser',
    name: 'Knowledge Codex',
    category: 'System',
    description: 'Browse system knowledge and schemas',
    icon: 'Database',
    status: 'active',
    vizType: 'GRID',
    summary: 'Browse system knowledge and schemas',
    promptProfile: 'Search knowledge',
    defaultConfig: { temperature: 0.1, topK: 1, topP: 1, maxSteps: 1 }
  },
  {
    id: 'agent-status',
    name: 'Agent Status',
    category: 'System',
    description: 'Monitor active agents',
    icon: 'Users',
    status: 'active',
    vizType: 'GRID',
    summary: 'Monitor active agents',
    promptProfile: 'Check agent status',
    defaultConfig: { temperature: 0.1, topK: 1, topP: 1, maxSteps: 1 }
  }
];