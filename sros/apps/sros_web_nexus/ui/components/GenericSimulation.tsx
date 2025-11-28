import React, { useEffect, useState, useRef, useCallback } from 'react';
import { SrosModuleDef, SimulationDataPoint, ModuleConfig } from '../types';
import { runKernelPrompt, runImageEditPrompt, runImageGenPrompt } from '../services/geminiService';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { Play, Pause, RefreshCw, Terminal as TerminalIcon, Activity, Image as ImageIcon, Upload, Wand2, Send, Loader2, Download, Settings, Sliders, X, Sparkles, Save, HardDriveDownload } from 'lucide-react';

interface GenericSimulationProps {
  moduleDef: SrosModuleDef;
}

const GenericSimulation: React.FC<GenericSimulationProps> = ({ moduleDef }) => {
  // Simulation State
  const [logs, setLogs] = useState<string[]>([]);
  const [data, setData] = useState<SimulationDataPoint[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [step, setStep] = useState(0);
  
  // Config State
  const [config, setConfig] = useState<ModuleConfig>(moduleDef.defaultConfig);
  const [showSettings, setShowSettings] = useState(false);
  
  // Image Editing State
  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const [editPrompt, setEditPrompt] = useState('');
  const [isProcessingImage, setIsProcessingImage] = useState(false);

  // Persistence State
  const [hasSave, setHasSave] = useState(false);
  
  // Refs
  const stepRef = useRef(0);
  const isRunningRef = useRef(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const configRef = useRef<ModuleConfig>(moduleDef.defaultConfig);

  // Sync config ref
  useEffect(() => {
    configRef.current = config;
  }, [config]);

  // Check for save file
  const checkSaveStatus = useCallback(() => {
      const saveKey = `sros_save_${moduleDef.id}`;
      setHasSave(!!localStorage.getItem(saveKey));
  }, [moduleDef.id]);

  // Initialize module state
  useEffect(() => {
    setLogs([
      `[BOOT] MODULE ${moduleDef.id.toUpperCase()} ONLINE`,
      `[LINK] BINDING SRX KERNEL TO ${moduleDef.name.toUpperCase()}`,
      `[INIT] READY...`
    ]);
    setData([]);
    setStep(0);
    setConfig(moduleDef.defaultConfig);
    setShowSettings(false);
    
    stepRef.current = 0;
    isRunningRef.current = false;
    setIsRunning(false);
    
    // Reset Image State
    setImageSrc(null);
    setEditPrompt('');
    setIsProcessingImage(false);

    // Check for existing save
    checkSaveStatus();

    if (timerRef.current) clearTimeout(timerRef.current);
  }, [moduleDef, checkSaveStatus]);

  // --- Persistence Logic ---

  const saveSimulation = () => {
      try {
          const saveKey = `sros_save_${moduleDef.id}`;
          const stateToSave = {
              logs,
              data,
              step,
              config,
              imageSrc,
              timestamp: Date.now()
          };
          localStorage.setItem(saveKey, JSON.stringify(stateToSave));
          setLogs(prev => [...prev, `[SYS] SNAPSHOT SAVED TO LOCAL STORAGE`]);
          setHasSave(true);
      } catch (e) {
          console.error("Save failed", e);
          setLogs(prev => [...prev, `[ERR] FAILED TO SAVE STATE`]);
      }
  };

  const loadSimulation = () => {
      try {
          const saveKey = `sros_save_${moduleDef.id}`;
          const raw = localStorage.getItem(saveKey);
          if (raw) {
              const state = JSON.parse(raw);
              
              // Restore State
              setLogs([...state.logs, `[SYS] STATE RESTORED FROM SNAPSHOT`]);
              setData(state.data);
              setStep(state.step);
              setConfig(state.config);
              setImageSrc(state.imageSrc || null);
              
              // Restore Refs (Critical for simulation loop continuity)
              stepRef.current = state.step;
              configRef.current = state.config;
              
              // Ensure simulation is paused on load to let user decide when to resume
              setIsRunning(false);
              isRunningRef.current = false;
              if (timerRef.current) clearTimeout(timerRef.current);
          }
      } catch (e) {
          console.error("Load failed", e);
          setLogs(prev => [...prev, `[ERR] CORRUPTED SAVE FILE`]);
      }
  };

  // --- Simulation Logic (Graph/Grid/Terminal) ---

  const runSimulationCycle = useCallback(async () => {
    if (!isRunningRef.current) return;

    const currentStep = stepRef.current;
    const currentConfig = configRef.current;

    // Check budget
    if (currentStep >= currentConfig.maxSteps) {
        setIsRunning(false);
        isRunningRef.current = false;
        setLogs(prev => [...prev, `[SYS] CYCLE LIMIT REACHED (${currentConfig.maxSteps})`, `[HALT] EXECUTION STOPPED`]);
        return;
    }
    
    // Construct prompt
    const prompt = `
      Role: SROS Physics / System Kernel for ${moduleDef.name}.
      Category: ${moduleDef.category}
      Summary: ${moduleDef.summary}
      Prompt Profile: ${moduleDef.promptProfile}
      Current Time Step: ${currentStep}
      
      TASK: Generate fake telemetry data for this module.
      
      OUTPUT FORMAT (STRICT JSON ONLY):
      {
        "logs": ["LOG: system status...", "LOG: metric update..."],
        "data": [
          { "v1": number, "v2": number },
          { "v1": number, "v2": number },
          { "v1": number, "v2": number }
        ]
      }
      
      Generate 3 data points. Ensure values evolve smoothly from previous state if possible.
    `;

    const result = await runKernelPrompt(prompt, currentConfig);

    if (result) {
      // Append logs
      setLogs(prev => [...prev, ...result.logs].slice(-20)); // Keep last 20 logs
      
      // Append data with timestamp mapping
      const newDataPoints = result.data.map((d, i) => ({
        ...d,
        t: currentStep + i
      }));
      
      setData(prev => [...prev, ...newDataPoints].slice(-50)); // Keep last 50 points
      
      stepRef.current += newDataPoints.length;
      setStep(stepRef.current);
    } else {
      setLogs(prev => [...prev, `[ERR] KERNEL FAULT - RETRYING`]);
    }

    // Schedule next cycle if still running
    if (isRunningRef.current) {
      timerRef.current = setTimeout(runSimulationCycle, 3000); // 3s loop
    }
  }, [moduleDef]);

  const toggleSimulation = () => {
    if (isRunning) {
      isRunningRef.current = false;
      setIsRunning(false);
      if (timerRef.current) clearTimeout(timerRef.current);
      setLogs(prev => [...prev, `[HALT] SIMULATION PAUSED`]);
    } else {
      // Check if we are already at limit
      if (stepRef.current >= config.maxSteps) {
         if (config.maxSteps === stepRef.current) {
             setLogs(prev => [...prev, `[WARN] BUDGET LIMIT REACHED. INCREASE MAX STEPS OR RESET.`]);
             return;
         }
      }

      isRunningRef.current = true;
      setIsRunning(true);
      setLogs(prev => [...prev, `[EXEC] KERNEL LOOP STARTED`]);
      runSimulationCycle();
    }
  };

  const resetSimulation = () => {
    isRunningRef.current = false;
    setIsRunning(false);
    if (timerRef.current) clearTimeout(timerRef.current);
    setLogs([`[RESET] MEMORY FLUSHED`, `[BOOT] READY`]);
    setData([]);
    setStep(0);
    stepRef.current = 0;
    setImageSrc(null);
    setEditPrompt('');
    // Re-check save status but don't clear the save file itself (user might want to reload it)
    checkSaveStatus();
  };

  const handleConfigChange = (key: keyof ModuleConfig, value: number) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  // --- Image Editing Logic ---

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result as string;
        setImageSrc(base64);
        setLogs(prev => [...prev, `[IMG] UPLOAD COMPLETE: ${file.name.toUpperCase()}`, `[SYS] READY FOR EDITING`]);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleImageAction = async () => {
    if (!editPrompt || isProcessingImage) return;

    setIsProcessingImage(true);

    try {
        if (imageSrc) {
            // Edit Mode (Gemini 2.5 Flash Image)
            setLogs(prev => [...prev, `[IMG] TRANSMITTING TO GEMINI 2.5...`, `[CMD] EDIT: "${editPrompt.toUpperCase()}"`]);
            const matches = imageSrc.match(/^data:(.+);base64,(.+)$/);
            if (!matches || matches.length !== 3) throw new Error("Invalid image data");
            const mimeType = matches[1];
            const base64Data = matches[2];

            const result = await runImageEditPrompt(base64Data, mimeType, editPrompt);
            if (result && result.imageBase64) {
               setImageSrc(`data:image/png;base64,${result.imageBase64}`);
               setLogs(prev => [...prev, `[IMG] RENDER COMPLETE`]);
            } else {
               setLogs(prev => [...prev, `[ERR] VISUAL SYNTHESIS FAILED`]);
            }
        } else {
            // Generation Mode (Gemini 3 Pro Image)
            setLogs(prev => [...prev, `[IMG] INITIALIZING HOLO-FORGE (GEMINI 3 PRO)...`, `[CMD] GEN: "${editPrompt.toUpperCase()}"`]);
            const result = await runImageGenPrompt(editPrompt);
            if (result && result.imageBase64) {
               setImageSrc(`data:image/png;base64,${result.imageBase64}`);
               setLogs(prev => [...prev, `[IMG] MATERIALIZATION COMPLETE`]);
            } else {
               setLogs(prev => [...prev, `[ERR] GENERATION FAILED`]);
            }
        }
    } catch (e) {
      setLogs(prev => [...prev, `[ERR] CRITICAL FAULT: ${e}`]);
    } finally {
      setIsProcessingImage(false);
      setEditPrompt('');
    }
  };

  const downloadImage = () => {
    if (!imageSrc) return;
    const link = document.createElement('a');
    link.href = imageSrc;
    link.download = `SROS_HOLO_FORGE_${Date.now()}.png`;
    link.click();
    setLogs(prev => [...prev, `[SYS] EXPORTED TO LOCAL STORAGE`]);
  };

  // --- Render Helpers ---

  const renderViz = () => {
    if (moduleDef.vizType === 'IMAGE') {
        return (
            <div className="h-full flex flex-col min-h-0">
                <div className="flex-1 relative bg-black/40 rounded-lg border border-dashed border-slate-700 flex items-center justify-center overflow-hidden group min-h-0">
                    {imageSrc ? (
                        <>
                            <img src={imageSrc} alt="Holo Forge" className="max-h-full max-w-full object-contain shadow-2xl animate-in fade-in zoom-in duration-500" />
                            <div className="absolute top-4 right-4 flex space-x-2 opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity">
                                <button 
                                    onClick={downloadImage}
                                    className="p-2 bg-black/60 text-white rounded hover:bg-cyan-500 hover:text-black transition-all border border-white/10"
                                    title="Download"
                                >
                                    <Download className="w-4 h-4" />
                                </button>
                                <button 
                                    onClick={() => fileInputRef.current?.click()}
                                    className="p-2 bg-black/60 text-white rounded hover:bg-cyan-500 hover:text-black transition-all border border-white/10"
                                    title="Replace Image"
                                >
                                    <Upload className="w-4 h-4" />
                                </button>
                            </div>
                        </>
                    ) : (
                        <div className="text-center p-8 max-w-md animate-in fade-in zoom-in duration-500">
                            <div className="mx-auto w-20 h-20 rounded-full bg-slate-900/80 flex items-center justify-center mb-6 border border-cyan-500/30 shadow-[0_0_30px_rgba(34,211,238,0.15)] relative">
                                <div className="absolute inset-0 rounded-full border border-cyan-500/10 animate-ping opacity-20"></div>
                                <ImageIcon className="w-10 h-10 text-cyan-400" />
                            </div>
                            <h3 className="text-white font-display font-bold text-lg mb-2 tracking-widest">HOLO FORGE ONLINE</h3>
                            <p className="text-cyan-400/60 font-mono text-xs mb-8 leading-relaxed">
                                Sovereign Image Synthesis Matrix active.<br/>
                                Enter a prompt to manifest visual data via Gemini 3 Pro, or upload source material for Gemini 2.5 editing.
                            </p>
                            <div className="flex justify-center gap-3">
                                <button 
                                    onClick={() => document.getElementById('holo-input')?.focus()}
                                    className="px-6 py-2.5 bg-cyan-500 text-slate-950 rounded hover:bg-cyan-400 transition-all font-mono text-xs font-bold tracking-widest flex items-center gap-2 shadow-[0_0_20px_rgba(34,211,238,0.3)] hover:shadow-[0_0_30px_rgba(34,211,238,0.5)]"
                                >
                                    <Sparkles className="w-4 h-4" /> TEXT TO IMAGE
                                </button>
                                <button 
                                    onClick={() => fileInputRef.current?.click()}
                                    className="px-6 py-2.5 bg-slate-800 border border-slate-700 text-slate-300 rounded hover:bg-slate-700 transition-all font-mono text-xs tracking-widest flex items-center gap-2 hover:text-white"
                                >
                                    <Upload className="w-4 h-4" /> UPLOAD SOURCE
                                </button>
                            </div>
                        </div>
                    )}
                    {isProcessingImage && (
                        <div className="absolute inset-0 bg-black/80 backdrop-blur-sm flex flex-col items-center justify-center z-10">
                            <div className="relative">
                                <div className="absolute inset-0 bg-cyan-500 blur-xl opacity-20 animate-pulse"></div>
                                <Loader2 className="relative w-16 h-16 text-cyan-400 animate-spin" />
                            </div>
                            <span className="mt-4 text-cyan-400 font-mono text-xs tracking-[0.2em] animate-pulse">
                                {imageSrc ? 'SYNTHESIZING EDITS...' : 'MATERIALIZING ASSET...'}
                            </span>
                        </div>
                    )}
                    <input 
                        type="file" 
                        ref={fileInputRef} 
                        onChange={handleFileUpload} 
                        className="hidden" 
                        accept="image/*"
                    />
                </div>
                
                <div className="mt-4 flex gap-2">
                    <div className="flex-1 relative group">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <Wand2 className={`w-4 h-4 transition-colors ${editPrompt ? 'text-cyan-400' : 'text-slate-500'}`} />
                        </div>
                        <input
                            id="holo-input"
                            type="text"
                            value={editPrompt}
                            onChange={(e) => setEditPrompt(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleImageAction()}
                            placeholder={imageSrc ? "Enter edit command (e.g. 'Add a retro filter')..." : "Enter prompt to generate image (e.g. 'Cyberpunk city')..."}
                            disabled={isProcessingImage}
                            className="block w-full pl-10 pr-3 py-3 bg-slate-900/50 border border-white/10 rounded text-sm text-slate-200 placeholder-slate-600 focus:ring-1 focus:ring-cyan-500/50 focus:border-cyan-500/50 focus:outline-none font-mono disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                        />
                        <div className="absolute inset-0 rounded border border-cyan-500/0 group-hover:border-cyan-500/20 pointer-events-none transition-colors"></div>
                    </div>
                    <button
                        onClick={handleImageAction}
                        disabled={!editPrompt || isProcessingImage}
                        className="px-4 md:px-6 bg-cyan-500 text-slate-950 font-bold rounded hover:bg-cyan-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center hover:shadow-[0_0_15px_rgba(34,211,238,0.4)]"
                    >
                        <Send className="w-4 h-4" />
                    </button>
                </div>
            </div>
        );
    }

    if (moduleDef.vizType === 'TERMINAL') {
      return (
        <div className="h-full bg-black/50 p-4 font-mono text-xs text-emerald-400 overflow-y-auto rounded-lg border border-white/5 shadow-inner custom-scrollbar">
           {logs.map((log, i) => (
             <div key={i} className="mb-1 border-b border-emerald-900/30 pb-1">
               <span className="text-slate-500 mr-2">[{new Date().toLocaleTimeString()}]</span>
               <span className="text-emerald-300 break-words">{log}</span>
             </div>
           ))}
           {isRunning && <div className="animate-pulse">_</div>}
        </div>
      );
    }
    
    // For GRAPH and GRID
    const ChartComponent = moduleDef.vizType === 'GRID' ? AreaChart : LineChart;
    
    return (
      <ResponsiveContainer width="100%" height="100%">
        <ChartComponent data={data}>
          <defs>
            <linearGradient id="colorV1" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#22d3ee" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="colorV2" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#818cf8" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#818cf8" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <XAxis dataKey="t" stroke="#475569" fontSize={10} tick={false} axisLine={false} />
          <YAxis stroke="#475569" fontSize={10} axisLine={false} tickLine={false} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '12px', borderRadius: '8px' }}
            itemStyle={{ color: '#e2e8f0' }}
            cursor={{ stroke: 'rgba(255,255,255,0.1)' }}
          />
          {moduleDef.vizType === 'GRID' ? (
             <>
              <Area type="monotone" dataKey="v1" stroke="#22d3ee" strokeWidth={2} fillOpacity={1} fill="url(#colorV1)" />
              <Area type="monotone" dataKey="v2" stroke="#818cf8" strokeWidth={2} fillOpacity={1} fill="url(#colorV2)" />
             </>
          ) : (
             <>
              <Line type="monotone" dataKey="v1" stroke="#22d3ee" strokeWidth={2} dot={false} activeDot={{ r: 4, fill: '#22d3ee' }} />
              <Line type="monotone" dataKey="v2" stroke="#818cf8" strokeWidth={2} dot={false} activeDot={{ r: 4, fill: '#818cf8' }} />
             </>
          )}
        </ChartComponent>
      </ResponsiveContainer>
    );
  };

  return (
    <div className="flex flex-col h-full bg-slate-900/40 backdrop-blur rounded-2xl border border-white/10 overflow-hidden shadow-2xl relative">
      {/* Background Grid FX */}
      <div className="absolute inset-0 z-0 opacity-10 pointer-events-none" 
             style={{
                 backgroundImage: 'linear-gradient(rgba(34, 211, 238, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(34, 211, 238, 0.1) 1px, transparent 1px)',
                 backgroundSize: '20px 20px'
             }}>
      </div>

      {/* Header */}
      <div className="relative z-10 p-4 border-b border-white/10 flex justify-between items-center bg-black/20">
        <div className="flex items-center space-x-3 overflow-hidden">
           <div className={`p-1.5 rounded bg-slate-800 flex-shrink-0 ${isRunning ? 'animate-pulse' : ''}`}>
               <Activity className="w-4 h-4 text-cyan-400" />
           </div>
           <div className="min-w-0">
               <span className="font-display text-sm font-bold text-slate-200 block leading-none truncate">{moduleDef.name}</span>
               <span className="text-[10px] text-slate-500 font-mono uppercase truncate block">ID: {moduleDef.id}</span>
           </div>
        </div>
        <div className="flex space-x-2 flex-shrink-0">
           {/* Save / Load Controls */}
           <div className="flex space-x-1 mr-2 border-r border-white/10 pr-2">
                <button 
                    onClick={saveSimulation}
                    className="p-2 rounded hover:bg-white/10 transition-colors border border-transparent hover:border-white/10 text-slate-400 hover:text-cyan-400"
                    title="Save Simulation State"
                >
                    <Save className="w-4 h-4" />
                </button>
                <button 
                    onClick={loadSimulation}
                    disabled={!hasSave}
                    className={`p-2 rounded transition-colors border border-transparent ${hasSave ? 'hover:bg-white/10 hover:border-white/10 text-slate-400 hover:text-emerald-400' : 'text-slate-700 cursor-not-allowed'}`}
                    title={hasSave ? "Load Saved State" : "No Saved State Found"}
                >
                    <HardDriveDownload className="w-4 h-4" />
                </button>
           </div>

           <button onClick={() => setShowSettings(!showSettings)} className={`p-2 rounded hover:bg-white/10 transition-colors border ${showSettings ? 'border-cyan-500/50 bg-cyan-500/10 text-cyan-400' : 'border-transparent text-slate-400'}`}>
              <Settings className="w-4 h-4" />
           </button>
           <div className="w-px h-6 bg-white/10 mx-1 self-center hidden md:block" />
           {moduleDef.vizType !== 'IMAGE' && (
             <button onClick={toggleSimulation} className="p-2 rounded hover:bg-white/10 transition-colors border border-transparent hover:border-white/10">
                {isRunning ? <Pause className="w-4 h-4 text-yellow-400" /> : <Play className="w-4 h-4 text-emerald-400" />}
             </button>
           )}
           <button onClick={resetSimulation} className="p-2 rounded hover:bg-white/10 transition-colors border border-transparent hover:border-white/10">
              <RefreshCw className="w-4 h-4 text-slate-400" />
           </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col p-4 space-y-4 overflow-hidden relative z-10">
        
        {/* Settings Overlay */}
        {showSettings && (
            <div className="absolute inset-0 md:inset-4 z-20 bg-slate-950/95 backdrop-blur-md border border-white/10 rounded-lg flex flex-col items-center justify-center animate-in fade-in zoom-in-95 duration-200 shadow-2xl p-4">
                <button onClick={() => setShowSettings(false)} className="absolute top-4 right-4 text-slate-500 hover:text-white transition-colors">
                    <X className="w-5 h-5" />
                </button>
                <div className="w-full max-w-sm space-y-6 md:space-y-8 p-2 md:p-6 overflow-y-auto max-h-full">
                    <div className="flex items-center justify-center space-x-3 mb-4">
                        <Sliders className="w-5 h-5 text-cyan-400" />
                        <h3 className="font-display text-base md:text-lg font-bold text-white tracking-widest uppercase">Kernel Parameters</h3>
                    </div>
                    
                    {/* Temperature */}
                    <div className="space-y-2">
                        <div className="flex justify-between text-xs font-mono text-slate-400 items-center">
                            <span>TEMPERATURE</span>
                            <input
                                type="number"
                                min="0" max="2" step="0.1"
                                value={config.temperature}
                                onChange={(e) => handleConfigChange('temperature', parseFloat(e.target.value))}
                                className="w-16 bg-slate-900 border border-slate-700 rounded px-1 text-right text-cyan-400 focus:outline-none focus:border-cyan-500 font-mono text-xs"
                            />
                        </div>
                        <input 
                            type="range" min="0" max="2" step="0.1" 
                            value={config.temperature}
                            onChange={(e) => handleConfigChange('temperature', parseFloat(e.target.value))}
                            className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                        />
                    </div>

                    {/* Top K */}
                    <div className="space-y-2">
                        <div className="flex justify-between text-xs font-mono text-slate-400 items-center">
                            <span>TOP K</span>
                            <input
                                type="number"
                                min="1" max="100" step="1"
                                value={config.topK}
                                onChange={(e) => handleConfigChange('topK', parseInt(e.target.value))}
                                className="w-16 bg-slate-900 border border-slate-700 rounded px-1 text-right text-cyan-400 focus:outline-none focus:border-cyan-500 font-mono text-xs"
                            />
                        </div>
                        <input 
                            type="range" min="1" max="100" step="1" 
                            value={config.topK}
                            onChange={(e) => handleConfigChange('topK', parseInt(e.target.value))}
                            className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                        />
                    </div>

                     {/* Top P */}
                     <div className="space-y-2">
                        <div className="flex justify-between text-xs font-mono text-slate-400 items-center">
                            <span>TOP P</span>
                            <input
                                type="number"
                                min="0" max="1" step="0.05"
                                value={config.topP}
                                onChange={(e) => handleConfigChange('topP', parseFloat(e.target.value))}
                                className="w-16 bg-slate-900 border border-slate-700 rounded px-1 text-right text-cyan-400 focus:outline-none focus:border-cyan-500 font-mono text-xs"
                            />
                        </div>
                        <input 
                            type="range" min="0" max="1" step="0.05" 
                            value={config.topP}
                            onChange={(e) => handleConfigChange('topP', parseFloat(e.target.value))}
                            className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                        />
                    </div>

                    {/* Max Steps */}
                    <div className="space-y-2">
                        <div className="flex justify-between text-xs font-mono text-slate-400 items-center">
                            <span>MAX STEPS</span>
                            <input
                                type="number"
                                min="10" max="1000" step="10"
                                value={config.maxSteps}
                                onChange={(e) => handleConfigChange('maxSteps', parseInt(e.target.value))}
                                className="w-16 bg-slate-900 border border-slate-700 rounded px-1 text-right text-cyan-400 focus:outline-none focus:border-cyan-500 font-mono text-xs"
                            />
                        </div>
                        <input 
                            type="range" min="10" max="1000" step="10" 
                            value={config.maxSteps}
                            onChange={(e) => handleConfigChange('maxSteps', parseInt(e.target.value))}
                            className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                        />
                    </div>
                </div>
            </div>
        )}

        {/* Viz Area */}
        <div className={`flex-1 rounded-lg border border-white/5 bg-slate-900/50 p-2 relative shadow-inner min-h-0 ${moduleDef.vizType === 'IMAGE' ? 'flex flex-col' : ''}`}>
             {data.length === 0 && moduleDef.vizType !== 'TERMINAL' && moduleDef.vizType !== 'IMAGE' && (
                 <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                        <div className="text-slate-700 font-mono text-xs mb-2">NO TELEMETRY DATA</div>
                        <div className="w-24 h-0.5 bg-slate-800 mx-auto"></div>
                    </div>
                 </div>
             )}
             {renderViz()}
        </div>

        {/* Logs Area (Mini console if not terminal viz) */}
        {moduleDef.vizType !== 'TERMINAL' && (
          <div className="h-32 bg-black/60 rounded-lg p-3 font-mono text-[10px] text-slate-400 overflow-y-auto border-t-2 border-cyan-500/30 custom-scrollbar shadow-lg flex-shrink-0">
             <div className="flex items-center space-x-2 mb-2 text-cyan-500 border-b border-white/5 pb-1">
                <TerminalIcon className="w-3 h-3" />
                <span className="font-bold">KERNEL LOG</span>
             </div>
             {logs.map((log, i) => (
                <div key={i} className="mb-0.5 whitespace-nowrap opacity-80 hover:opacity-100 transition-opacity">
                    <span className="text-slate-600 mr-2">{'>'}</span>
                    {log}
                </div>
             ))}
             {isRunning && <span className="animate-pulse text-cyan-500">_</span>}
          </div>
        )}
      </div>
      
      {/* Stats Footer */}
      <div className="px-4 py-2 bg-black/40 border-t border-white/5 flex justify-between text-[10px] font-mono text-slate-500 z-10">
          <span className="flex items-center gap-2">
            <span className={`w-1.5 h-1.5 rounded-full ${isRunning || isProcessingImage ? 'bg-emerald-500 animate-pulse' : 'bg-slate-700'}`}></span>
            STEP: {step}
          </span>
          <span className="hidden md:inline">LATENCY: {isRunning || isProcessingImage ? Math.floor(Math.random() * 20 + 40) : 0}ms</span>
          <span>BUDGET: {config.maxSteps}</span>
      </div>
    </div>
  );
};

export default GenericSimulation;