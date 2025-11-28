import React, { useState } from 'react';
import { SrosModuleDef } from '../types';
import GenericSimulation from './GenericSimulation';
import { Download, Maximize, Play, Image as ImageIcon } from 'lucide-react';

interface RealityPanelProps {
  activeModule: SrosModuleDef | null;
  agentMedia: { url: string; type: 'IMAGE' | 'VIDEO' } | null;
}

const RealityPanel: React.FC<RealityPanelProps> = ({ activeModule, agentMedia }) => {
  const [isPlaying, setIsPlaying] = useState(false);

  // 1. Module Simulation (Standard SROS Mode)
  if (activeModule) {
    return (
      <div className="h-full p-4 pl-0">
        <GenericSimulation moduleDef={activeModule} />
      </div>
    );
  }

  // 2. Agent Media Viewer (Sovereign Holo Deck)
  if (agentMedia) {
      return (
          <div className="h-full p-4 pl-0 flex flex-col">
              <div className="flex-1 rounded-2xl border border-white/10 bg-black/60 overflow-hidden relative group">
                   {/* Background Grid */}
                   <div className="absolute inset-0 z-0 opacity-20 pointer-events-none" 
                        style={{
                            backgroundImage: 'linear-gradient(rgba(34, 211, 238, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(34, 211, 238, 0.1) 1px, transparent 1px)',
                            backgroundSize: '40px 40px'
                        }}>
                   </div>

                   {/* Content */}
                   <div className="absolute inset-0 flex items-center justify-center p-8">
                       {agentMedia.type === 'IMAGE' ? (
                           <img src={agentMedia.url} alt="Holo Gen" className="max-w-full max-h-full object-contain shadow-[0_0_50px_rgba(0,0,0,0.5)] rounded-lg animate-in zoom-in duration-500" />
                       ) : (
                           <video src={agentMedia.url} controls autoPlay className="max-w-full max-h-full object-contain shadow-2xl rounded-lg border border-white/10" />
                       )}
                   </div>

                   {/* Overlay UI */}
                   <div className="absolute top-0 left-0 right-0 p-4 bg-gradient-to-b from-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                       <div className="flex justify-between items-center">
                           <div className="flex items-center space-x-2">
                               {agentMedia.type === 'IMAGE' ? <ImageIcon className="w-4 h-4 text-cyan-400" /> : <Play className="w-4 h-4 text-pink-400" />}
                               <span className="text-xs font-mono text-white tracking-widest uppercase">{agentMedia.type} PREVIEW</span>
                           </div>
                           <button className="p-2 bg-white/10 hover:bg-white/20 rounded text-white transition-colors">
                               <Download className="w-4 h-4" />
                           </button>
                       </div>
                   </div>
              </div>
          </div>
      );
  }

  // 3. Idle State (Sovereign Standby)
  return (
    <div className="h-full p-4 pl-0">
        <div className="h-full rounded-2xl border border-dashed border-slate-800 flex flex-col items-center justify-center bg-slate-950/30 text-slate-700 relative overflow-hidden">
           <div className="absolute inset-0 opacity-10 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-slate-700 via-slate-900 to-transparent"></div>
           <div className="text-[120px] font-display font-bold opacity-5 select-none animate-pulse">SROS</div>
           <div className="absolute bottom-10 left-0 right-0 text-center">
               <p className="font-mono text-xs tracking-[0.3em] uppercase text-slate-600 mb-2">Awaiting Visual Protocol</p>
               <div className="flex justify-center gap-1">
                   <span className="w-1 h-1 bg-slate-600 rounded-full animate-bounce delay-75"></span>
                   <span className="w-1 h-1 bg-slate-600 rounded-full animate-bounce delay-150"></span>
                   <span className="w-1 h-1 bg-slate-600 rounded-full animate-bounce delay-300"></span>
               </div>
           </div>
        </div>
    </div>
  );
};

export default RealityPanel;