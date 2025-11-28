import React, { useEffect, useState } from 'react';
import { api, KnowledgePack } from '../services/api';
import { Database, Search, FileCode, Box, Layers } from 'lucide-react';

const KnowledgePanel: React.FC = () => {
    const [packs, setPacks] = useState<KnowledgePack[]>([]);
    const [loading, setLoading] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');

    const fetchPacks = async () => {
        setLoading(true);
        try {
            const data = await api.getKnowledgePacks();
            setPacks(data);
        } catch (error) {
            console.error("Failed to fetch knowledge packs", error);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!searchQuery.trim()) {
            fetchPacks();
            return;
        }
        setLoading(true);
        try {
            const results = await api.searchKnowledge(searchQuery);
            setPacks(results);
        } catch (error) {
            console.error("Search failed", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPacks();
    }, []);

    return (
        <div className="flex flex-col h-full bg-slate-900/50 backdrop-blur-sm p-6 overflow-hidden">
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <Database className="w-6 h-6 text-emerald-400" />
                    <h2 className="text-xl font-display font-bold text-white tracking-wide">KNOWLEDGE CODEX</h2>
                </div>
                <form onSubmit={handleSearch} className="flex gap-2">
                    <div className="relative">
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="Search schemas..."
                            className="bg-black/30 border border-white/10 rounded-lg px-4 py-2 pl-10 text-sm text-white focus:outline-none focus:border-emerald-500/50 w-64"
                        />
                        <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                    </div>
                </form>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 overflow-y-auto pr-2 custom-scrollbar">
                {packs.map((pack) => (
                    <div key={pack.id} className="bg-black/30 border border-white/5 rounded-lg p-4 hover:border-emerald-500/30 transition-colors group">
                        <div className="flex items-start justify-between mb-3">
                            <div className="flex items-center gap-2">
                                <Box className="w-4 h-4 text-emerald-500/70" />
                                <h3 className="font-bold text-slate-200 text-sm truncate w-40" title={pack.name}>
                                    {pack.name}
                                </h3>
                            </div>
                            <span className="text-[10px] bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20">
                                SCHEMA
                            </span>
                        </div>

                        <div className="space-y-2 mb-4">
                            <div className="flex items-center gap-2 text-xs text-slate-500">
                                <FileCode className="w-3 h-3" />
                                <span className="truncate">{pack.id}</span>
                            </div>
                            {pack.metadata?.source && (
                                <div className="flex items-center gap-2 text-xs text-slate-500">
                                    <Layers className="w-3 h-3" />
                                    <span className="truncate">{pack.metadata.source.split('\\').pop()}</span>
                                </div>
                            )}
                        </div>

                        <div className="mt-2 pt-2 border-t border-white/5">
                            <pre className="text-[10px] text-slate-400 font-mono overflow-hidden h-20 opacity-50 group-hover:opacity-100 transition-opacity">
                                {JSON.stringify(pack.content, null, 2)}
                            </pre>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default KnowledgePanel;
