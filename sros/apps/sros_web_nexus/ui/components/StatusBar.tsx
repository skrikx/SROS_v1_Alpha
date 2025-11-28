import React from 'react';

const StatusBar: React.FC = () => {
  return (
    <footer className="h-8 bg-black/80 backdrop-blur text-white flex items-center justify-between px-4 border-t border-white/10 text-[10px] font-mono uppercase tracking-widest z-50">
      <div className="flex items-center space-x-6">
        <div className="flex items-center space-x-2 text-cyan-400">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            <span>SROS ONLINE</span>
        </div>
        <span className="text-slate-500 hidden md:inline">RUNTIME: GEMINI-3-PRO (EMULATED)</span>
        <span className="text-slate-500 hidden sm:inline">ROUTE: SROS_V1_SECURE</span>
      </div>
      
      <div className="hidden md:flex items-center space-x-6 text-slate-600">
        <span>MEM: 64TB</span>
        <span>NET: 120PB/s</span>
        <span>SEC: MAX</span>
      </div>
    </footer>
  );
};

export default StatusBar;