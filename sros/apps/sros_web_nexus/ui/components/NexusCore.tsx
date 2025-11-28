import React, { useState, useEffect, useRef } from 'react';
import { SrosModuleDef, AgentMessage, AgentState } from '../types';
import { Mic, Send, Image as ImageIcon, Video, BrainCircuit, Globe, MapPin, Zap, Bot, Loader2, Sparkles, StopCircle, Terminal, Command, Paperclip, X, Settings, Volume2, Radio, AlertTriangle } from 'lucide-react';
import { runAgentChat, generateHoloImage, generateVeoVideo, connectLiveSession, editHoloImage, generateSpeech, playAudio } from '../services/geminiService';
import { api } from '../services/api';
import LogPanel from './LogPanel';
import RouterPanel from './RouterPanel';
import KnowledgePanel from './KnowledgePanel';
import AgentsPanel from './AgentsPanel';

interface NexusCoreProps {
    activeModule: SrosModuleDef | null;
    onAgentMediaGenerated?: (url: string, type: 'IMAGE' | 'VIDEO') => void;
}

const NexusCore: React.FC<NexusCoreProps> = ({ activeModule, onAgentMediaGenerated }) => {
    // --- Agent State ---
    const [messages, setMessages] = useState<AgentMessage[]>([
        { id: '0', role: 'system', content: 'SROS PRIME AGENT ONLINE. SOVEREIGN MODE ACTIVE.', timestamp: Date.now(), type: 'TEXT' }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [attachment, setAttachment] = useState<{ data: string; mimeType: string; name: string } | null>(null);
    const [showConfig, setShowConfig] = useState(false);

    // Error State
    const [error, setError] = useState<string | null>(null);

    const [agentState, setAgentState] = useState<AgentState>({
        isThinking: false,
        isListening: false,
        isSpeaking: false,
        mode: 'STANDARD',
        grounding: { search: false, maps: false },
        thinkingBudget: 0,
        config: {
            imageSize: '1K',
            imageAspectRatio: '16:9',
            videoAspectRatio: '16:9',
            temperature: 0.7,
            topK: 40,
            topP: 0.95,
            systemInstruction: 'You are SROS Prime, a sovereign AI interface. Be concise, mythic, and helpful.'
        }
    });

    // Voice State
    const [liveSessionActive, setLiveSessionActive] = useState(false);
    const cleanupLiveRef = useRef<(() => void) | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const nextStartTimeRef = useRef<number>(0);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Scrolling
    const scrollRef = useRef<HTMLDivElement>(null);
    useEffect(() => {
        if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }, [messages]);

    // --- Actions ---

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setAttachment({
                    data: reader.result as string,
                    mimeType: file.type,
                    name: file.name
                });
            };
            reader.readAsDataURL(file);
        }
    };

    const handleSendMessage = async () => {
        if (!inputValue.trim() && !agentState.isListening && !attachment) return;
        setError(null); // Clear previous errors

        // Determine user message type for visual feedback
        let msgType: 'TEXT' | 'IMAGE' | 'VIDEO' = 'TEXT';
        let mediaUrl = undefined;
        if (attachment) {
            msgType = attachment.mimeType.startsWith('image/') ? 'IMAGE' : 'VIDEO';
            mediaUrl = attachment.data;
        }

        const userMsg: AgentMessage = {
            id: Date.now().toString(),
            role: 'user',
            content: inputValue || (attachment ? `[Attached ${attachment.name}]` : ''),
            timestamp: Date.now(),
            type: msgType,
            mediaUrl: mediaUrl
        };

        setMessages(prev => [...prev, userMsg]);
        setInputValue('');
        const currentAttachment = attachment;
        setAttachment(null);
        setAgentState(prev => ({ ...prev, isThinking: true }));

        try {
            // Command Routing
            const lowerInput = userMsg.content.toLowerCase();

            // 1. Video Generation Intent
            if (agentState.mode === 'VEO' || lowerInput.includes('generate video') || lowerInput.includes('create a video')) {
                const prompt = userMsg.content.replace(/generate video|create a video/gi, '').trim();
                const videoUrl = await generateVeoVideo(
                    prompt || "Abstract cybernetic flow",
                    agentState.config.videoAspectRatio,
                    currentAttachment?.data // Pass image if attached for Image-to-Video
                );
                if (videoUrl) {
                    if (onAgentMediaGenerated) onAgentMediaGenerated(videoUrl, 'VIDEO');
                    setMessages(prev => [...prev, {
                        id: Date.now().toString(),
                        role: 'model',
                        content: `Veo Render Complete: "${prompt}"`,
                        timestamp: Date.now(),
                        type: 'VIDEO',
                        mediaUrl: videoUrl
                    }]);
                } else {
                    setMessages(prev => [...prev, { id: Date.now().toString(), role: 'model', content: "Veo Generation Failed.", timestamp: Date.now(), type: 'TEXT' }]);
                }
                setAgentState(prev => ({ ...prev, isThinking: false }));
                return;
            }

            // 2. Image Generation / Editing Intent
            if (agentState.mode === 'HOLO' || lowerInput.includes('generate image') || lowerInput.includes('create an image') || lowerInput.includes('edit')) {
                // EDITING
                if (currentAttachment && lowerInput.includes('edit')) {
                    const prompt = userMsg.content.replace(/edit/gi, '').trim();
                    const imgUrl = await editHoloImage(currentAttachment.data, prompt || "Enhance");
                    if (imgUrl) {
                        if (onAgentMediaGenerated) onAgentMediaGenerated(imgUrl, 'IMAGE');
                        setMessages(prev => [...prev, {
                            id: Date.now().toString(),
                            role: 'model',
                            content: `Holo Edit Complete: "${prompt}"`,
                            timestamp: Date.now(),
                            type: 'IMAGE',
                            mediaUrl: imgUrl
                        }]);
                    } else {
                        setMessages(prev => [...prev, { id: Date.now().toString(), role: 'model', content: "Holo Edit Failed.", timestamp: Date.now(), type: 'TEXT' }]);
                    }
                }
                // GENERATION
                else {
                    const prompt = userMsg.content.replace(/generate image|create an image/gi, '').trim();
                    const imgUrl = await generateHoloImage(
                        prompt || "Abstract neon structure",
                        agentState.config.imageSize,
                        agentState.config.imageAspectRatio
                    );
                    if (imgUrl) {
                        if (onAgentMediaGenerated) onAgentMediaGenerated(imgUrl, 'IMAGE');
                        setMessages(prev => [...prev, {
                            id: Date.now().toString(),
                            role: 'model',
                            content: `Holo Render Complete: "${prompt}"`,
                            timestamp: Date.now(),
                            type: 'IMAGE',
                            mediaUrl: imgUrl
                        }]);
                    } else {
                        setMessages(prev => [...prev, { id: Date.now().toString(), role: 'model', content: "Holo Generation Failed.", timestamp: Date.now(), type: 'TEXT' }]);
                    }
                }
                setAgentState(prev => ({ ...prev, isThinking: false }));
                return;
                return;
            }

            // 3. Evolution Intent
            if (lowerInput.includes('sr::evolve') || lowerInput.includes('trigger evolution')) {
                setMessages(prev => [...prev, {
                    id: Date.now().toString(),
                    role: 'model',
                    content: "Initiating Ouroboros Evolution Cycle...",
                    timestamp: Date.now(),
                    type: 'TEXT'
                }]);

                const result = await api.triggerEvolution();

                let content = "Evolution Cycle Complete.\n";
                if (result.status === 'success') {
                    content += `Generated ${result.proposals_count} proposals.\n`;
                    if (result.proposals && result.proposals.length > 0) {
                        content += "Proposals:\n" + result.proposals.map((p: string) => `- ${p}`).join('\n');
                    } else {
                        content += "No viable improvements found in this cycle.";
                    }
                } else {
                    content += `Failed: ${result.message || result.detail || "Unknown Error"}`;
                }

                setMessages(prev => [...prev, {
                    id: Date.now().toString(),
                    role: 'model',
                    content: content,
                    timestamp: Date.now(),
                    type: 'TEXT'
                }]);

                setAgentState(prev => ({ ...prev, isThinking: false }));
                return;
            }

            // 4. Standard/Thinking/Grounding/Vision Chat (Via Skrikx Backend)
            // We now route through the backend Skrikx agent which uses the Kernel

            // Check if it's a direct agent run command
            if (lowerInput.startsWith('run ') || lowerInput.startsWith('status scan')) {
                const response = await api.runAgent('architect', userMsg.content);
                if (response.status === 'success') {
                    setMessages(prev => [...prev, {
                        id: Date.now().toString(),
                        role: 'model',
                        content: typeof response.result === 'string' ? response.result : JSON.stringify(response.result, null, 2),
                        timestamp: Date.now(),
                        type: 'TEXT'
                    }]);
                } else {
                    throw new Error(response.detail || "Agent Execution Failed");
                }
            } else {
                // Default Chat
                const response = await api.skrikxChat(userMsg.content, {
                    session_id: 'nexus_session',
                    agent_state: agentState
                });

                if (response.status === 'success') {
                    const result = response.response;
                    setMessages(prev => [...prev, {
                        id: Date.now().toString(),
                        role: 'model',
                        content: result.text,
                        timestamp: Date.now(),
                        type: 'TEXT',
                        metadata: { groundingSources: result.sources as any }
                    }]);
                } else {
                    // Fallback for now if chat endpoint isn't ready
                    setMessages(prev => [...prev, {
                        id: Date.now().toString(),
                        role: 'model',
                        content: "SROS Prime: Command acknowledged. (Backend chat pending)",
                        timestamp: Date.now(),
                        type: 'TEXT'
                    }]);
                }
            }

        } catch (e: any) {
            console.error("Agent Execution Error:", e);
            setError(e.message || "An unexpected error occurred during execution.");
            setMessages(prev => [...prev, { id: Date.now().toString(), role: 'model', content: "CRITICAL FAILURE: Protocol execution interrupted.", timestamp: Date.now(), type: 'TEXT' }]);
        } finally {
            setAgentState(prev => ({ ...prev, isThinking: false }));
        }
    };

    const handleSpeak = async (text: string) => {
        try {
            const audio = await generateSpeech(text);
            if (audio) playAudio(audio);
        } catch (e) {
            setError("TTS Subsystem Failure");
        }
    };

    const toggleLiveSession = async () => {
        if (liveSessionActive) {
            // Stop
            if (cleanupLiveRef.current) cleanupLiveRef.current();
            if (audioContextRef.current) audioContextRef.current.close();
            setLiveSessionActive(false);
            setAgentState(prev => ({ ...prev, mode: 'STANDARD' }));
        } else {
            // Start
            setLiveSessionActive(true);
            setAgentState(prev => ({ ...prev, mode: 'LIVE' }));

            // Init audio out
            audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 24000 });
            nextStartTimeRef.current = audioContextRef.current.currentTime;

            try {
                const cleanup = await connectLiveSession(
                    (audioBuffer) => {
                        // Play Audio
                        if (!audioContextRef.current) return;
                        const ctx = audioContextRef.current;
                        const source = ctx.createBufferSource();
                        source.buffer = audioBuffer;
                        source.connect(ctx.destination);

                        const now = ctx.currentTime;
                        // Schedule
                        const startTime = Math.max(now, nextStartTimeRef.current);
                        source.start(startTime);
                        nextStartTimeRef.current = startTime + audioBuffer.duration;
                    },
                    (text, isUser) => {
                        setMessages(prev => [...prev, {
                            id: Date.now().toString(),
                            role: isUser ? 'user' : 'model',
                            content: text,
                            timestamp: Date.now(),
                            type: 'TEXT'
                        }]);
                    },
                    (err) => {
                        console.error(err);
                        setLiveSessionActive(false);
                        setError("Live Uplink Terminated: " + (err.message || "Connection Lost"));
                    }
                );
                cleanupLiveRef.current = cleanup;
            } catch (e: any) {
                console.error("Failed to start Live", e);
                setLiveSessionActive(false);
                setError(e.message || "Failed to initialize Live Session. Check permissions.");
            }
        }
    };

    // --- Render ---

    if (activeModule) {
        // --- Module Specific Views ---
        if (activeModule.id === 'logs') return <LogPanel />;
        if (activeModule.id === 'router') return <RouterPanel />;
        if (activeModule.id === 'knowledge-browser') return <KnowledgePanel />;
        if (activeModule.id === 'agent-status') return <AgentsPanel />;

        // --- Legacy Module View (Collapsed Header) ---
        return (
            <div className="flex flex-col h-full relative overflow-hidden bg-slate-900/50 backdrop-blur-sm">
                <header className="p-4 border-b border-white/10 flex justify-between items-center">
                    <div className="flex items-center space-x-3">
                        <Command className="w-5 h-5 text-cyan-400" />
                        <h2 className="font-display font-bold text-white tracking-widest">{activeModule.name}</h2>
                    </div>
                    <span className="text-[10px] font-mono text-emerald-500 uppercase">Module Active</span>
                </header>
                <div className="p-4 flex-1 overflow-auto">
                    <p className="font-mono text-xs text-slate-400">{activeModule.summary}</p>
                    <div className="mt-4 p-2 bg-black/40 rounded border border-white/5">
                        <div className="text-[10px] text-slate-500 mb-1">PROMPT PROFILE</div>
                        <code className="text-xs text-cyan-300">{activeModule.promptProfile}</code>
                    </div>
                </div>
            </div>
        );
    }

    // --- SROS PRIME AGENT INTERFACE ---
    return (
        <div className="flex flex-col h-full relative overflow-hidden bg-slate-950/80 backdrop-blur-xl">
            {/* Dynamic Background */}
            <div className="absolute inset-0 z-0 pointer-events-none">
                <div className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] rounded-full blur-[100px] transition-all duration-1000 ${liveSessionActive ? 'bg-emerald-900/20' : agentState.isThinking ? 'bg-purple-900/20' : 'bg-cyan-900/10'}`}></div>
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20"></div>
            </div>

            {/* Error Alert */}
            {error && (
                <div className="absolute top-20 left-1/2 -translate-x-1/2 z-50 bg-red-900/90 border border-red-500 text-white px-4 py-2 rounded shadow-xl flex items-center gap-2 animate-in fade-in slide-in-from-top-5">
                    <AlertTriangle className="w-4 h-4" />
                    <span className="text-xs font-mono">{error}</span>
                    <button onClick={() => setError(null)} className="hover:text-red-300 ml-2"><X className="w-3 h-3" /></button>
                </div>
            )}

            {/* Header */}
            <header className="relative z-10 p-6 border-b border-white/5 flex items-center justify-between">
                <div className="flex items-center space-x-4">
                    <div className={`w-10 h-10 rounded-full border border-white/10 flex items-center justify-center transition-all duration-500 ${liveSessionActive ? 'bg-emerald-500/10 shadow-[0_0_30px_rgba(16,185,129,0.3)]' : agentState.isThinking ? 'bg-purple-500/10 shadow-[0_0_30px_rgba(168,85,247,0.3)]' : 'bg-cyan-500/10 shadow-[0_0_20px_rgba(34,211,238,0.2)]'}`}>
                        <Bot className={`w-5 h-5 ${liveSessionActive ? 'text-emerald-400' : 'text-cyan-400'}`} />
                    </div>
                    <div>
                        <h1 className="font-display font-bold text-xl text-white tracking-widest flex items-center gap-2">
                            SROS PRIME
                            {liveSessionActive ? (
                                <div className="flex items-center gap-2 px-2 py-0.5 rounded bg-emerald-500/20 border border-emerald-500/50">
                                    <span className="relative flex h-2 w-2">
                                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                        <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                                    </span>
                                    <span className="text-[10px] text-emerald-400 font-mono animate-pulse">LIVE UPLINK ACTIVE</span>
                                </div>
                            ) : (
                                agentState.mode !== 'STANDARD' && <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/10 text-cyan-300 font-mono">{agentState.mode}</span>
                            )}
                        </h1>
                        <p className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">Multi-Modal Sovereign Intelligence</p>
                    </div>
                </div>
                <div className="flex items-center space-x-2">
                    <button
                        onClick={() => setShowConfig(!showConfig)}
                        className={`p-2 rounded-full border border-white/10 hover:bg-white/5 text-slate-400 transition-colors ${showConfig ? 'bg-white/10 text-white' : ''}`}
                    >
                        <Settings className="w-4 h-4" />
                    </button>
                    {/* Live Button */}
                    <button
                        onClick={toggleLiveSession}
                        className={`flex items-center space-x-2 px-4 py-2 rounded-full border transition-all duration-300 ${liveSessionActive
                            ? 'bg-emerald-500/20 border-emerald-500 text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.3)]'
                            : 'border-white/10 hover:bg-white/5 text-slate-400'
                            }`}
                    >
                        {liveSessionActive ? (
                            <>
                                <StopCircle className="w-4 h-4 animate-pulse" />
                                <span className="text-xs font-bold font-display tracking-wider">TERMINATE UPLINK</span>
                            </>
                        ) : (
                            <>
                                <Mic className="w-4 h-4" />
                                <span className="text-xs font-bold font-display tracking-wider">CONNECT LIVE</span>
                            </>
                        )}
                    </button>
                </div>
            </header>

            {/* Config Popover */}
            {showConfig && (
                <div className="absolute top-20 right-6 z-30 w-80 bg-slate-900 border border-white/10 rounded-lg p-4 shadow-2xl animate-in fade-in zoom-in-95 overflow-y-auto max-h-[80vh] custom-scrollbar">
                    <div className="flex justify-between items-center mb-4 border-b border-white/5 pb-2">
                        <span className="text-xs font-display font-bold text-cyan-400 uppercase tracking-widest">System Config</span>
                        <button onClick={() => setShowConfig(false)}><X className="w-4 h-4 text-slate-500 hover:text-white" /></button>
                    </div>

                    <div className="space-y-4">
                        {/* System Prompt */}
                        <div>
                            <label className="text-[10px] text-slate-500 font-mono block mb-1">SYSTEM INSTRUCTION</label>
                            <textarea
                                value={agentState.config.systemInstruction}
                                onChange={(e) => setAgentState(p => ({ ...p, config: { ...p.config, systemInstruction: e.target.value } }))}
                                className="w-full bg-black/50 border border-white/10 text-xs text-white rounded p-2 font-mono h-20 resize-none focus:outline-none focus:border-cyan-500/50"
                            />
                        </div>

                        {/* Generation Parameters */}
                        <div className="grid grid-cols-2 gap-3">
                            <div>
                                <label className="text-[10px] text-slate-500 font-mono block mb-1">TEMP</label>
                                <input
                                    type="number"
                                    min="0" max="2" step="0.1"
                                    value={agentState.config.temperature}
                                    onChange={(e) => setAgentState(p => ({ ...p, config: { ...p.config, temperature: parseFloat(e.target.value) } }))}
                                    className="w-full bg-black/50 border border-white/10 text-xs text-white rounded p-1 font-mono text-center focus:outline-none focus:border-cyan-500/50"
                                />
                            </div>
                            <div>
                                <label className="text-[10px] text-slate-500 font-mono block mb-1">TOP K</label>
                                <input
                                    type="number"
                                    min="1" max="100" step="1"
                                    value={agentState.config.topK}
                                    onChange={(e) => setAgentState(p => ({ ...p, config: { ...p.config, topK: parseInt(e.target.value) } }))}
                                    className="w-full bg-black/50 border border-white/10 text-xs text-white rounded p-1 font-mono text-center focus:outline-none focus:border-cyan-500/50"
                                />
                            </div>
                            <div>
                                <label className="text-[10px] text-slate-500 font-mono block mb-1">TOP P</label>
                                <input
                                    type="number"
                                    min="0" max="1" step="0.05"
                                    value={agentState.config.topP}
                                    onChange={(e) => setAgentState(p => ({ ...p, config: { ...p.config, topP: parseFloat(e.target.value) } }))}
                                    className="w-full bg-black/50 border border-white/10 text-xs text-white rounded p-1 font-mono text-center focus:outline-none focus:border-cyan-500/50"
                                />
                            </div>
                        </div>

                        <div className="border-t border-white/5 pt-2">
                            <div className="text-[10px] text-slate-500 font-mono mb-2 uppercase">Media Config</div>
                            <div>
                                <label className="text-[10px] text-slate-500 font-mono block mb-1">IMAGE SIZE</label>
                                <div className="grid grid-cols-3 gap-1 mb-2">
                                    {['1K', '2K', '4K'].map(size => (
                                        <button
                                            key={size}
                                            onClick={() => setAgentState(p => ({ ...p, config: { ...p.config, imageSize: size as any } }))}
                                            className={`text-[10px] py-1 border rounded ${agentState.config.imageSize === size ? 'bg-cyan-500/20 border-cyan-500 text-cyan-300' : 'border-white/10 text-slate-400 hover:bg-white/5'}`}
                                        >
                                            {size}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            <div className="mb-2">
                                <label className="text-[10px] text-slate-500 font-mono block mb-1">IMAGE RATIO</label>
                                <select
                                    value={agentState.config.imageAspectRatio}
                                    onChange={(e) => setAgentState(p => ({ ...p, config: { ...p.config, imageAspectRatio: e.target.value as any } }))}
                                    className="w-full bg-black/50 border border-white/10 text-xs text-white rounded p-1 font-mono focus:outline-none focus:border-cyan-500/50"
                                >
                                    <option value="1:1">1:1 (Square)</option>
                                    <option value="16:9">16:9 (Landscape)</option>
                                    <option value="9:16">9:16 (Portrait)</option>
                                    <option value="4:3">4:3 (Classic)</option>
                                    <option value="3:4">3:4 (Vertical)</option>
                                </select>
                            </div>
                            <div>
                                <label className="text-[10px] text-slate-500 font-mono block mb-1">VIDEO RATIO</label>
                                <div className="grid grid-cols-2 gap-1">
                                    {['16:9', '9:16'].map(ratio => (
                                        <button
                                            key={ratio}
                                            onClick={() => setAgentState(p => ({ ...p, config: { ...p.config, videoAspectRatio: ratio as any } }))}
                                            className={`text-[10px] py-1 border rounded ${agentState.config.videoAspectRatio === ratio ? 'bg-pink-500/20 border-pink-500 text-pink-300' : 'border-white/10 text-slate-400 hover:bg-white/5'}`}
                                        >
                                            {ratio}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Chat Stream */}
            <main className="flex-1 overflow-y-auto p-6 space-y-6 relative z-10 custom-scrollbar" ref={scrollRef}>
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full opacity-30 space-y-4">
                        <div className="w-20 h-20 rounded-full border-2 border-dashed border-cyan-500 animate-[spin_10s_linear_infinite]" />
                        <p className="font-mono text-xs tracking-[0.2em] text-cyan-400">AWAITING INPUT</p>
                    </div>
                )}

                {messages.map((msg) => (
                    <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[80%] rounded-2xl p-4 border backdrop-blur-md ${msg.role === 'user'
                            ? 'bg-cyan-950/30 border-cyan-800/30 text-cyan-50 rounded-tr-none'
                            : msg.role === 'system'
                                ? 'bg-red-900/10 border-red-500/20 text-red-400 font-mono text-xs w-full text-center'
                                : 'bg-slate-900/60 border-white/10 text-slate-200 rounded-tl-none'
                            }`}>
                            {msg.role !== 'system' && (
                                <div className="flex items-center justify-between gap-4 mb-2 opacity-50 text-[10px] font-mono uppercase">
                                    <div className="flex gap-2">
                                        <span>{msg.role === 'user' ? 'OPERATOR' : 'SROS PRIME'}</span>
                                        <span>{new Date(msg.timestamp).toLocaleTimeString()}</span>
                                    </div>
                                    {msg.role === 'model' && msg.type === 'TEXT' && (
                                        <button onClick={() => handleSpeak(msg.content)} className="hover:text-cyan-400"><Volume2 className="w-3 h-3" /></button>
                                    )}
                                </div>
                            )}

                            {msg.type === 'TEXT' && <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>}
                            {msg.type === 'IMAGE' && (
                                <div className="space-y-2">
                                    <p className="text-xs text-slate-400 italic mb-2">{msg.content}</p>
                                    <div className="rounded-lg overflow-hidden border border-white/10">
                                        <img src={msg.mediaUrl} alt="Agent Gen" className="w-full h-auto" />
                                    </div>
                                </div>
                            )}
                            {msg.type === 'VIDEO' && (
                                <div className="space-y-2">
                                    <p className="text-xs text-slate-400 italic mb-2">{msg.content}</p>
                                    <video src={msg.mediaUrl} controls className="w-full rounded-lg border border-white/10" />
                                </div>
                            )}
                            {msg.type === 'AUDIO' && (
                                <div className="space-y-2">
                                    <p className="text-xs text-slate-400 italic mb-2">{msg.content}</p>
                                    <div className="flex items-center gap-2 p-3 bg-slate-900/50 rounded-lg border border-white/10">
                                        <Radio className="w-4 h-4 text-emerald-400" />
                                        <span className="text-xs font-mono text-emerald-300">AUDIO DATA RECEIVED</span>
                                    </div>
                                </div>
                            )}

                            {/* Sources */}
                            {msg.metadata?.groundingSources && msg.metadata.groundingSources.length > 0 && (
                                <div className="mt-3 pt-3 border-t border-white/5">
                                    <div className="text-[10px] font-mono text-slate-500 mb-1">GROUNDING SOURCES</div>
                                    <div className="flex flex-wrap gap-2">
                                        {msg.metadata.groundingSources.map((source, idx) => (
                                            <a key={idx} href={source.uri} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-[10px] bg-black/40 px-2 py-1 rounded text-cyan-400 hover:text-cyan-300 truncate max-w-[200px]">
                                                <Globe className="w-3 h-3" /> {source.title}
                                            </a>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {agentState.isThinking && (
                    <div className="flex justify-start animate-pulse">
                        <div className="bg-slate-900/60 border border-white/10 p-4 rounded-2xl rounded-tl-none flex items-center space-x-3">
                            {agentState.mode === 'SOVEREIGN' ? <BrainCircuit className="w-4 h-4 text-purple-400 animate-spin" /> : <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />}
                            <span className="text-xs font-mono text-slate-400">
                                {agentState.mode === 'SOVEREIGN' ? 'DEEP THINKING (GEMINI 3 PRO)...' : 'PROCESSING...'}
                            </span>
                        </div>
                    </div>
                )}
            </main>

            {/* Input Deck */}
            <div className="p-4 relative z-20 bg-slate-950/50 backdrop-blur-lg border-t border-white/10">
                {/* Attachment Preview */}
                {attachment && (
                    <div className="absolute bottom-full left-4 mb-2 p-2 bg-slate-900 border border-white/10 rounded flex items-center gap-2 animate-in slide-in-from-bottom-2">
                        <div className="w-8 h-8 bg-slate-800 rounded flex items-center justify-center">
                            {attachment.mimeType.startsWith('image') ? <ImageIcon className="w-4 h-4 text-cyan-400" /> : <Video className="w-4 h-4 text-pink-400" />}
                        </div>
                        <span className="text-xs text-slate-300 max-w-[150px] truncate">{attachment.name}</span>
                        <button onClick={() => setAttachment(null)} className="p-1 hover:bg-white/10 rounded"><X className="w-3 h-3 text-slate-500" /></button>
                    </div>
                )}

                {/* Toolbar */}
                <div className="flex items-center space-x-2 mb-3 px-1">
                    <button
                        onClick={() => setAgentState(prev => ({ ...prev, mode: prev.mode === 'SOVEREIGN' ? 'STANDARD' : 'SOVEREIGN' }))}
                        className={`p-2 rounded text-[10px] font-bold flex items-center gap-1 transition-colors border ${agentState.mode === 'SOVEREIGN' ? 'bg-purple-500/20 text-purple-300 border-purple-500/50' : 'bg-slate-900 text-slate-500 border-white/5 hover:border-white/10'}`}
                        title="Enable Thinking Model (Gemini 3 Pro)"
                    >
                        <BrainCircuit className="w-3 h-3" /> SOVEREIGN
                    </button>
                    <div className="w-px h-4 bg-white/10 mx-1" />
                    <button
                        onClick={() => setAgentState(prev => ({ ...prev, grounding: { ...prev.grounding, search: !prev.grounding.search } }))}
                        className={`p-2 rounded text-[10px] font-bold flex items-center gap-1 transition-colors border ${agentState.grounding.search ? 'bg-blue-500/20 text-blue-300 border-blue-500/50' : 'bg-slate-900 text-slate-500 border-white/5 hover:border-white/10'}`}
                    >
                        <Globe className="w-3 h-3" /> NET
                    </button>
                    <button
                        onClick={() => setAgentState(prev => ({ ...prev, grounding: { ...prev.grounding, maps: !prev.grounding.maps } }))}
                        className={`p-2 rounded text-[10px] font-bold flex items-center gap-1 transition-colors border ${agentState.grounding.maps ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50' : 'bg-slate-900 text-slate-500 border-white/5 hover:border-white/10'}`}
                    >
                        <MapPin className="w-3 h-3" /> MAP
                    </button>
                    <div className="w-px h-4 bg-white/10 mx-1" />
                    <button
                        onClick={() => setAgentState(prev => ({ ...prev, mode: prev.mode === 'VEO' ? 'STANDARD' : 'VEO' }))}
                        className={`p-2 rounded text-[10px] font-bold flex items-center gap-1 transition-colors border ${agentState.mode === 'VEO' ? 'bg-pink-500/20 text-pink-300 border-pink-500/50' : 'bg-slate-900 text-slate-500 border-white/5 hover:border-white/10'}`}
                    >
                        <Video className="w-3 h-3" /> VEO
                    </button>
                    <button
                        onClick={() => setAgentState(prev => ({ ...prev, mode: prev.mode === 'HOLO' ? 'STANDARD' : 'HOLO' }))}
                        className={`p-2 rounded text-[10px] font-bold flex items-center gap-1 transition-colors border ${agentState.mode === 'HOLO' ? 'bg-orange-500/20 text-orange-300 border-orange-500/50' : 'bg-slate-900 text-slate-500 border-white/5 hover:border-white/10'}`}
                    >
                        <ImageIcon className="w-3 h-3" /> HOLO
                    </button>
                </div>

                {/* Input Area */}
                <div className="relative group">
                    <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-lg blur opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                    <div className={`relative flex items-center bg-black/60 border rounded-lg overflow-hidden transition-all duration-500 ${liveSessionActive ? 'border-emerald-500/50 shadow-[0_0_20px_rgba(16,185,129,0.2)]' : 'border-white/10 focus-within:border-cyan-500/50'}`}>
                        <button
                            onClick={() => fileInputRef.current?.click()}
                            className="pl-3 text-slate-400 hover:text-cyan-400 transition-colors"
                        >
                            <Paperclip className="w-4 h-4" />
                        </button>
                        <input
                            type="file"
                            ref={fileInputRef}
                            className="hidden"
                            onChange={handleFileUpload}
                            accept="image/*,video/*"
                        />
                        <input
                            type="text"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                            placeholder={liveSessionActive ? "Voice Uplink Active..." : "Enter Command Sequence..."}
                            className="flex-1 bg-transparent border-none text-sm text-white placeholder-slate-600 focus:ring-0 py-3 px-3 font-mono"
                            disabled={liveSessionActive}
                        />
                        {liveSessionActive ? (
                            <div className="p-3 text-emerald-400 animate-pulse">
                                <Radio className="w-4 h-4" />
                            </div>
                        ) : (
                            <button
                                onClick={handleSendMessage}
                                disabled={!inputValue.trim() && !attachment}
                                className="p-3 text-cyan-400 hover:text-white hover:bg-white/10 transition-colors disabled:opacity-50"
                            >
                                <Send className="w-4 h-4" />
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default NexusCore;