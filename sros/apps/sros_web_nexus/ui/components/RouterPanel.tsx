import React, { useEffect, useState } from 'react';
import { api, Task } from '../services/api';
import { Terminal, Play, RefreshCw, CheckCircle, XCircle, Clock } from 'lucide-react';

const RouterPanel: React.FC = () => {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [newTask, setNewTask] = useState('');
    const [loading, setLoading] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [result, setResult] = useState<any>(null);

    const fetchTasks = async () => {
        setLoading(true);
        try {
            const data = await api.getRouterTasks();
            setTasks(data);
        } catch (error) {
            console.error("Failed to fetch tasks", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTasks();
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newTask.trim()) return;

        setSubmitting(true);
        try {
            const response = await api.submitRoutedTask(newTask);
            setResult(response);
            setNewTask('');
            fetchTasks();
        } catch (error) {
            console.error("Failed to submit task", error);
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="flex flex-col h-full bg-slate-900/50 backdrop-blur-sm p-6 overflow-hidden">
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <Terminal className="w-6 h-6 text-cyan-400" />
                    <h2 className="text-xl font-display font-bold text-white tracking-wide">TASK ROUTER</h2>
                </div>
                <button
                    onClick={fetchTasks}
                    className="p-2 hover:bg-white/5 rounded-lg text-cyan-400 transition-colors"
                    disabled={loading}
                >
                    <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                </button>
            </div>

            {/* Input Area */}
            <div className="mb-8">
                <form onSubmit={handleSubmit} className="relative">
                    <input
                        type="text"
                        value={newTask}
                        onChange={(e) => setNewTask(e.target.value)}
                        placeholder="Enter a task for the SROS Router..."
                        className="w-full bg-slate-950/50 border border-white/10 rounded-xl py-4 pl-5 pr-14 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all"
                    />
                    <button
                        type="submit"
                        disabled={submitting || !newTask.trim()}
                        className="absolute right-2 top-2 bottom-2 px-4 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 disabled:hover:bg-cyan-600 text-white rounded-lg transition-colors flex items-center justify-center"
                    >
                        {submitting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
                    </button>
                </form>
            </div>

            {/* Result Display */}
            {result && (
                <div className="mb-8 p-4 bg-slate-950/80 border border-cyan-900/30 rounded-lg font-mono text-sm">
                    <div className="flex items-center gap-2 mb-2 text-cyan-400">
                        <CheckCircle className="w-4 h-4" />
                        <span className="font-bold">LAST RESULT</span>
                    </div>
                    <pre className="whitespace-pre-wrap text-slate-300 overflow-x-auto">
                        {JSON.stringify(result, null, 2)}
                    </pre>
                </div>
            )}

            {/* Task List */}
            <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
                <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-4">Recent Tasks</h3>

                {tasks.length === 0 ? (
                    <div className="text-center py-12 text-slate-600 italic">
                        No routed tasks found.
                    </div>
                ) : (
                    <div className="space-y-3">
                        {tasks.map((task, idx) => (
                            <div key={idx} className="p-4 bg-white/5 border border-white/5 rounded-lg hover:border-white/10 transition-colors">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="font-mono text-xs text-cyan-400">{task.task_id}</span>
                                    <span className={`text-xs px-2 py-0.5 rounded-full ${task.status === 'success' ? 'bg-green-500/20 text-green-400' : 'bg-slate-700 text-slate-400'
                                        }`}>
                                        {task.status}
                                    </span>
                                </div>
                                {task.result && (
                                    <div className="text-sm text-slate-400 line-clamp-2">
                                        {typeof task.result === 'string' ? task.result : JSON.stringify(task.result)}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default RouterPanel;
