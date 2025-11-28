import React, { useEffect, useState } from 'react';
import { api, LogEntry } from '../services/api';
import { FileText, RefreshCw, AlertTriangle, Info, CheckCircle } from 'lucide-react';

const LogPanel: React.FC = () => {
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [loading, setLoading] = useState(false);

    const fetchLogs = async () => {
        setLoading(true);
        try {
            const data = await api.getLogs();
            setLogs(data);
        } catch (error) {
            console.error("Failed to fetch logs", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLogs();
        const interval = setInterval(fetchLogs, 5000);
        return () => clearInterval(interval);
    }, []);

    const getIcon = (level: string) => {
        switch (level.toLowerCase()) {
            case 'error': return <AlertTriangle className="w-4 h-4 text-red-400" />;
            case 'warning': return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
            case 'success': return <CheckCircle className="w-4 h-4 text-green-400" />;
            default: return <Info className="w-4 h-4 text-blue-400" />;
        }
    };

    return (
        <div className="flex flex-col h-full bg-slate-900/50 backdrop-blur-sm p-6 overflow-hidden">
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <FileText className="w-6 h-6 text-cyan-400" />
                    <h2 className="text-xl font-display font-bold text-white tracking-wide">SYSTEM LOGS</h2>
                </div>
                <button
                    onClick={fetchLogs}
                    className="p-2 hover:bg-white/5 rounded-lg text-cyan-400 transition-colors"
                    disabled={loading}
                >
                    <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                </button>
            </div>

            <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar bg-black/30 rounded-lg p-4 font-mono text-xs">
                {logs.length === 0 ? (
                    <div className="text-center py-12 text-slate-600 italic">
                        No logs available.
                    </div>
                ) : (
                    <div className="space-y-1">
                        {logs.map((log, idx) => (
                            <div key={idx} className="flex gap-3 hover:bg-white/5 p-1 rounded transition-colors">
                                <span className="text-slate-500 whitespace-nowrap">{log.timestamp}</span>
                                <span className="flex-shrink-0 pt-0.5">{getIcon(log.level || 'info')}</span>
                                <span className="text-slate-300 break-all">{log.message}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default LogPanel;
