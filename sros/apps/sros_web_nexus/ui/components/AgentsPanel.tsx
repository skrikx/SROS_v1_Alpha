import React, { useEffect, useState } from 'react';
import { api, Agent } from '../services/api';
import { Users, Activity, Cpu, Shield, Zap } from 'lucide-react';

const AgentsPanel: React.FC = () => {
    const [agents, setAgents] = useState<Agent[]>([]);
    const [loading, setLoading] = useState(false);

    const fetchAgents = async () => {
        setLoading(true);
        try {
            const data = await api.getAgents();
            setAgents(data);
        } catch (error) {
            console.error("Failed to fetch agents", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAgents();
    }, []);

    const handleInvoke = async (agentName: string) => {
        const task = window.prompt(`Assign task to ${agentName}:`, "Report status");
        if (!task) return;

        try {
            // Optimistic UI update or toast could go here
            console.log(`Invoking ${agentName} with task: ${task}`);
            const result = await api.runAgent(agentName, task);
            alert(`Result from ${agentName}:\n${JSON.stringify(result.result, null, 2)}`);
        } catch (error) {
            console.error("Agent invocation failed", error);
            alert("Failed to invoke agent. Check console for details.");
        }
    };

    return (
        <div className="flex flex-col h-full bg-slate-900/50 backdrop-blur-sm p-6 overflow-hidden">
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <Users className="w-6 h-6 text-purple-400" />
                    <h2 className="text-xl font-display font-bold text-white tracking-wide">AGENT STATUS</h2>
                </div>
                <button
                    onClick={fetchAgents}
                    className="p-2 hover:bg-white/5 rounded-lg text-purple-400 transition-colors"
                >
                    <Activity className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {agents.map((agent, idx) => (
                    <div key={idx} className="bg-black/30 border border-white/5 rounded-lg p-5 hover:border-purple-500/30 transition-colors relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-2 opacity-10">
                            <Cpu className="w-24 h-24 text-purple-500" />
                        </div>

                        <div className="relative z-10">
                            <div className="flex items-center justify-between mb-4">
                                <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center border border-purple-500/30">
                                    <Shield className="w-5 h-5 text-purple-400" />
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                                    <span className="text-xs font-bold text-emerald-500 tracking-wider">ONLINE</span>
                                </div>
                            </div>

                            <h3 className="text-lg font-bold text-white mb-1">{agent.name}</h3>
                            <p className="text-sm text-purple-400/80 font-mono mb-4">{agent.role}</p>

                            <div className="space-y-2">
                                <div className="flex justify-between text-xs">
                                    <span className="text-slate-500">Status</span>
                                    <span className="text-slate-300">Idle</span>
                                </div>
                                <div className="w-full bg-white/5 rounded-full h-1">
                                    <div className="bg-purple-500 h-1 rounded-full w-0" />
                                </div>
                                <div className="flex justify-between text-xs pt-2">
                                    <span className="text-slate-500">Tasks Completed</span>
                                    <span className="text-slate-300 font-mono">0</span>
                                </div>
                            </div>

                            <div className="mt-4 pt-4 border-t border-white/5 flex gap-2">
                                <button
                                    onClick={() => handleInvoke(agent.name)}
                                    className="flex-1 bg-white/5 hover:bg-purple-500/20 text-xs text-slate-300 hover:text-white py-2 rounded border border-white/5 hover:border-purple-500/30 transition-all flex items-center justify-center gap-2"
                                >
                                    <Zap className="w-3 h-3" />
                                    Invoke
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default AgentsPanel;
