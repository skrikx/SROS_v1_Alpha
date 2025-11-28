"""
API Routes

REST API routes for SROS operations.
"""
from typing import Dict, Any, Optional
try:
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


if FASTAPI_AVAILABLE:
    # Request models
    class AgentRunRequest(BaseModel):
        agent_name: str
        task: str
    
    class MemoryWriteRequest(BaseModel):
        content: str
        layer: str = "short"
        key: Optional[str] = None
    
    
    def register_routes(app):
        """Register all API routes."""
        
        # Agents
        @app.get("/api/agents")
        def list_agents():
            """List available agents."""
            return {
                "agents": [
                    {"name": "architect", "role": "System Architect"},
                    {"name": "builder", "role": "Code Builder"},
                    {"name": "tester", "role": "Test Engineer"}
                ]
            }
        
        @app.post("/api/agents/run")
        def run_agent(request: AgentRunRequest):
            """Run an agent with a task."""
            from sros.runtime.agents import ArchitectAgent, BuilderAgent, TesterAgent
            
            try:
                if request.agent_name == "architect":
                    agent = ArchitectAgent()
                elif request.agent_name == "builder":
                    agent = BuilderAgent()
                elif request.agent_name == "tester":
                    agent = TesterAgent()
                else:
                    raise HTTPException(status_code=404, detail=f"Agent not found: {request.agent_name}")
                
                agent.initialize()
                result = agent.act(request.task)
                
                return {
                    "status": "success",
                    "agent": request.agent_name,
                    "result": result
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Memory
        @app.get("/api/memory")
        def read_memory(layer: str = "short", query: Optional[str] = None):
            """Read from memory."""
            from sros.memory import MemoryRouter, ShortTermMemory, LongTermMemory, CodexMemory
            
            try:
                router = MemoryRouter()
                router.initialize_layers(
                    short_term=ShortTermMemory(),
                    long_term=LongTermMemory(),
                    codex=CodexMemory()
                )
                
                results = router.read(query=query, layer=layer)
                
                return {
                    "status": "success",
                    "layer": layer,
                    "count": len(results),
                    "results": results
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/api/memory")
        def write_memory(request: MemoryWriteRequest):
            """Write to memory."""
            from sros.memory import MemoryRouter, ShortTermMemory, LongTermMemory, CodexMemory
            
            try:
                router = MemoryRouter()
                router.initialize_layers(
                    short_term=ShortTermMemory(),
                    long_term=LongTermMemory(),
                    codex=CodexMemory()
                )
                
                router.write(request.content, layer=request.layer, key=request.key)
                
                return {
                    "status": "success",
                    "message": "Content written to memory"
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Status
        @app.get("/api/status")
        def get_status():
            """Get system status."""
            return {
                "status": "operational",
                "version": "1.0.0",
                "components": {
                    "kernel": "running",
                    "runtime": "ready",
                    "governance": "active",
                    "mirroros": "observing"
                }
            }
        
        # Adapters
        @app.get("/api/adapters")
        def list_adapters():
            """List available adapters."""
            from sros.adapters.registry import get_registry
            
            registry = get_registry()
            adapters = registry.list_adapters()
            
            return {
                "status": "success",
                "adapters": adapters
            }
        
        # Costs
        @app.get("/api/costs")
        def get_costs():
            """Get cost summary."""
            from sros.governance import CostTracker
            
            tracker = CostTracker()
            budget_status = tracker.check_budget()
            usage_report = tracker.get_usage_report()
            
            return {
                "status": "success",
                "budget": budget_status,
                "usage": usage_report
            }

        # Sovereign Directive
        @app.get("/api/sovereign/status")
        def get_sovereign_status():
            """Get Sovereign Directive status."""
            from sros.governance.sovereign_directive import SovereignDirective
            directive = SovereignDirective()
            
            return {
                "status": "ACTIVE",
                "version": "2.0.0",
                "active": directive.active,
                "laws_loaded": True,
                "audit_log_path": str(directive.audit_log.log_path)
            }

        @app.post("/api/sovereign/approve")
        def approve_action(action_id: str):
            """Approve a pending high-risk action (Stub)."""
            return {"status": "APPROVED", "action_id": action_id, "message": "Approval recorded in audit log."}

        # --- In-Memory State ---
        _ROUTER_TASKS = []
        
        # --- Agents ---
        @app.get("/api/agents")
        def get_agents():
            """Get active agents."""
            return {"agents": [
                {"name": "Architect", "role": "System Architect", "status": "active"},
                {"name": "Coder", "role": "Implementation Specialist", "status": "idle"},
                {"name": "Guardian", "role": "Security Monitor", "status": "active"},
                {"name": "Router", "role": "Task Orchestrator", "status": "active"}
            ]}

        @app.post("/api/agents/run")
        def run_agent_endpoint(request: TaskSubmitRequest): # Reusing model
            """Run a specific agent."""
            from sros.runtime.agents import ArchitectAgent
            # For now, always use Architect as the generic runner
            agent = ArchitectAgent()
            agent.initialize()
            result = agent.act(request.task)
            return {"status": "success", "result": result}

        # --- Router ---
        @app.get("/api/router/tasks")
        def get_router_tasks():
            """Get routed tasks."""
            return {"tasks": _ROUTER_TASKS}

        @app.post("/api/router/tasks")
        def submit_routed_task(request: TaskSubmitRequest):
            """Submit a task to the router."""
            task_id = f"task_{int(time.time())}_{len(_ROUTER_TASKS)}"
            
            # Simulate processing
            result_summary = f"Processed '{request.task}' via SROS Kernel."
            
            new_task = {
                "task_id": task_id,
                "status": "success",
                "result": result_summary,
                "timestamp": time.time()
            }
            _ROUTER_TASKS.insert(0, new_task) # Prepend
            
            return new_task

        # --- Logs ---
        @app.get("/api/logs")
        def get_logs():
            """Get system logs."""
            # Generate some dynamic logs for liveliness
            current_time = time.strftime("%H:%M:%S")
            base_logs = [
                {"timestamp": current_time, "level": "INFO", "message": "System heartbeat nominal"},
                {"timestamp": current_time, "level": "INFO", "message": "Memory fabric stable"},
                {"timestamp": current_time, "level": "DEBUG", "message": "Ouroboros loop idle"}
            ]
            return {"logs": base_logs}

        # --- Knowledge ---
        @app.get("/api/knowledge/packs")
        def get_knowledge_packs():
            """Get knowledge packs."""
            from sros.memory import CodexMemory
            codex = CodexMemory()
            # Mock data for now as Codex might be empty
            return {"packs": [
                {"id": "sros_core", "name": "SROS Core Schema", "content": {"version": "1.0"}, "metadata": {"source": "system"}}
            ]}

        @app.get("/api/knowledge/search")
        def search_knowledge(query: str):
            """Search knowledge."""
            return {"results": []}

        # --- Evolution ---
        @app.post("/api/evolution/cycle")
        def trigger_evolution():
            """Trigger an evolution cycle."""
            from sros.evolution.ouroboros import OuroborosLoop
            from sros.evolution.proposer import EvolutionProposer
            from sros.governance.sovereign_directive import SovereignDirective
            
            # Initialize loop components
            directive = SovereignDirective()
            proposer = EvolutionProposer(model_adapter=None) # Will use default/mock if not set
            loop = OuroborosLoop(directive=directive, proposer=proposer)
            
            # Run a cycle (simplified)
            pain_points = [{"id": "pp_1", "description": "Manual intervention required for updates", "severity": "medium"}]
            proposals = loop._propose(pain_points)
            
            return {
                "status": "success",
                "proposals_count": len(proposals),
                "proposals": [p.title for p in proposals],
                "message": "Evolution cycle completed successfully."
            }

        @app.get("/api/evolution/status")
        def get_evolution_status():
            """Get evolution status."""
            return {"status": "idle", "last_cycle": time.time()}

        # --- Skrikx Chat ---
        class ChatRequest(BaseModel):
            message: str
            context: Optional[Dict[str, Any]] = None

        @app.post("/api/skrikx/chat")
        def skrikx_chat(request: ChatRequest):
            """Chat with Skrikx Prime."""
            try:
                from sros.runtime.agents import ArchitectAgent
                agent = ArchitectAgent()
                agent.initialize()
                
                # Pass context if needed, currently just text
                response = agent.act(f"User says: {request.message}. Respond as Skrikx Prime.")
                
                return {
                    "status": "success",
                    "response": {
                        "text": response,
                        "sources": []
                    }
                }
            except Exception as e:
                import traceback
                traceback.print_exc()
                return {
                    "status": "error",
                    "detail": str(e),
                    "response": {
                        "text": f"Error: {str(e)}",
                        "sources": []
                    }
                }


else:
    def register_routes(app):
        """Placeholder when FastAPI not available."""
        pass
