import React from 'react';
import { SROS_MODULE_REGISTRY } from '../constants';
import { SrosModuleDef, ModuleCategory } from '../types';
import { Hexagon, Activity, Box, Database, Terminal, Cpu, X } from 'lucide-react';

interface SidebarNavProps {
  selectedModuleId: string | null;
  onSelectModule: (id: string) => void;
  isOpen?: boolean;
  onClose?: () => void;
}

const CATEGORY_ICONS: Record<ModuleCategory, React.ReactNode> = {
  Physics: <Activity className="w-4 h-4" />,
  Research: <Database className="w-4 h-4" />,
  Automation: <Cpu className="w-4 h-4" />,
  Visuals: <Box className="w-4 h-4" />,
  System: <Terminal className="w-4 h-4" />,
};

const SidebarNav: React.FC<SidebarNavProps> = ({ selectedModuleId, onSelectModule, isOpen = false, onClose }) => {
  const groupedModules = React.useMemo(() => {
    const groups: Partial<Record<ModuleCategory, SrosModuleDef[]>> = {};
    SROS_MODULE_REGISTRY.forEach((mod) => {
      if (!groups[mod.category]) groups[mod.category] = [];
      groups[mod.category]?.push(mod);
    });
    return groups;
  }, []);

  return (
    <>
      {/* Mobile Backdrop */}
      <div 
        className={`fixed inset-0 bg-black/80 backdrop-blur-sm z-40 md:hidden transition-opacity duration-300 ${isOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Sidebar Container */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-72 md:w-64 bg-slate-950/95 backdrop-blur-xl md:bg-slate-900/80 md:backdrop-blur-md 
        border-r border-white/10 flex flex-col transform transition-transform duration-300 ease-in-out
        md:relative md:translate-x-0
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="p-6 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Hexagon className="w-8 h-8 text-cyan-400 fill-cyan-400/10 animate-pulse" />
            <div>
              <h1 className="font-display font-bold text-lg text-white tracking-widest">SROS</h1>
              <p className="text-[10px] text-cyan-400 font-mono tracking-wider">OMNI NEXUS v1.0</p>
            </div>
          </div>
          <button 
            onClick={onClose} 
            className="md:hidden p-2 -mr-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <nav className="flex-1 p-4 space-y-6 overflow-y-auto custom-scrollbar">
          {(Object.keys(groupedModules) as ModuleCategory[]).map((category) => (
            <div key={category}>
              <div className="flex items-center space-x-2 mb-2 px-2">
                <span className="text-cyan-400/70">{CATEGORY_ICONS[category]}</span>
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest font-display">
                  {category}
                </h3>
              </div>
              <ul className="space-y-1">
                {groupedModules[category]?.map((mod) => (
                  <li key={mod.id}>
                    <button
                      onClick={() => onSelectModule(mod.id)}
                      className={`w-full text-left px-3 py-2.5 md:py-2 rounded-lg text-sm font-medium transition-all duration-200 border border-transparent
                        ${
                          selectedModuleId === mod.id
                            ? 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30 shadow-[0_0_15px_rgba(34,211,238,0.1)]'
                            : 'text-slate-400 hover:text-white hover:bg-white/5'
                        }
                      `}
                    >
                      {mod.name}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </nav>
        
        <div className="p-4 border-t border-white/10 bg-slate-900/50">
          <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono">
            <span>IDENTITY</span>
            <span className="text-emerald-500 flex items-center gap-1">
              <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
              SRX ACE
            </span>
          </div>
        </div>
      </div>
    </>
  );
};

export default SidebarNav;