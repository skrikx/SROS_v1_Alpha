import sys
import os
import json
import time
import asyncio
import logging
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent.parent
sys.path.append(str(repo_root))

from sros.srxml.parser import SRXMLParser
from sros.kernel import kernel_bootstrap
from sros.kernel.event_bus import EventBus
from sros.memory.memory_router import MemoryRouter
from sros.runtime.workflow_engine import WorkflowEngine
from sros.governance.policy_engine import PolicyEngine
from sros.mirroros.witness import Witness
from sros.mirroros.trace_store import TraceStore
from sros.nexus.nexus_core import NexusCore
from sros.adapters.models.gemini_adapter import GeminiAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("harness.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SROS_Harness")

class StubGeminiAdapter(GeminiAdapter):
    def generate(self, prompt: str, tools=None, stream=False):
        return {
            "text": f"Simulated response for: {prompt[:20]}...",
            "usage": {"total_tokens": 10},
            "finish_reason": "stop"
        }

def run_test(name, func):
    logger.info(f"--- START TEST: {name} ---")
    try:
        func()
        logger.info(f"--- PASS: {name} ---\n")
        return True
    except Exception as e:
        logger.error(f"--- FAIL: {name} ---")
        logger.exception(e)
        return False

def test_parser_srxml():
    parser = SRXMLParser()
    workflow_path = repo_root / "tests/fixtures/sample_workflow.srxml"
    agent_path = repo_root / "tests/fixtures/sample_agent_prompt.srxml"
    
    workflow = parser.parse(str(workflow_path))
    assert workflow['tag'] == 'workflow'
    # Children might be a list or dict depending on parser logic, but let's check content
    # With my update, children are in the dict.
    # <step> elements would be under 'step' key
    assert 'step' in workflow
    
    agent = parser.parse(str(agent_path))
    assert agent['tag'] == 'agent'
    assert agent['name']['#text'] == 'Test Agent'

def test_kernel_bootstrap():
    kernel = kernel_bootstrap.boot()
    assert kernel.event_bus is not None
    assert kernel.registry is not None
    # Shutdown
    kernel.registry.stop_all()

def test_memory_router():
    router = MemoryRouter()
    seed_path = repo_root / "tests/fixtures/memory_seed.json"
    with open(seed_path, 'r') as f:
        seeds = json.load(f)
    
    # Load seeds
    for seed in seeds:
        router.write(seed['content'], layer=seed['layer'], metadata={"id": seed['id']})
    
    # Read back
    results = router.read("Seeded", layer="short")
    assert len(results) > 0
    assert "Seeded memory 1" in results[0]['content']

def test_workflow_engine():
    # Setup
    event_bus = EventBus()
    global shared_trace_store
    witness = Witness(shared_trace_store)
    # Inject stub adapter
    adapter = StubGeminiAdapter()
    
    engine = WorkflowEngine(event_bus, witness)
    # Monkey patch or inject adapter if possible. 
    # For now, WorkflowEngine might use a default agent which uses default adapter.
    # We will rely on the engine's ability to run.
    
    workflow_path = repo_root / "tests/fixtures/sample_workflow.srxml"
    parser = SRXMLParser()
    workflow_def = parser.parse(str(workflow_path))
    
    # Run
    asyncio.run(engine.execute(workflow_def, context={"test": True}))
    
    # Verify trace
    # (Assuming witness wrote to file)

def test_governance_policy():
    engine = PolicyEngine()
    # Load fake policy
    policy_path = repo_root / "tests/fixtures/policies/allow_all.json"
    with open(policy_path, 'r') as f:
        policy = json.load(f)
    
    engine.load_policy(policy)
    result = engine.evaluate("some_action", {})
    assert result.allowed == True

def test_mirroros_trace():
    global shared_trace_store
    # We expect traces from previous workflow test
    traces = shared_trace_store.load_recent(10)
    assert len(traces) > 0

def test_nexus_dryrun():
    nexus = NexusCore()
    # Inject stub
    nexus.llm_adapter = StubGeminiAdapter()
    
    result = nexus.run_command("demo.seeded", payload={"fake": True})
    assert result['status'] == 'success'

if __name__ == "__main__":
    # Initialize shared trace store
    shared_trace_store = TraceStore(str(repo_root / "sros_traces.jsonl"))
    
    tests = [
        ("parser.srxml", test_parser_srxml),
        ("kernel.bootstrap", test_kernel_bootstrap),
        ("memory.router", test_memory_router),
        ("workflow.engine", test_workflow_engine),
        ("governance.policy", test_governance_policy),
        ("mirroros.trace", test_mirroros_trace),
        ("nexus.dryrun", test_nexus_dryrun)
    ]
    
    passed = 0
    for name, func in tests:
        if run_test(name, func):
            passed += 1
            
    logger.info(f"Summary: {passed}/{len(tests)} tests passed.")
    if passed == len(tests):
        sys.exit(0)
    else:
        sys.exit(1)
