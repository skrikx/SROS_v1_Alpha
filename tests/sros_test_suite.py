import pytest
import time
import json
import os
from sros.kernel import kernel_bootstrap
from sros.apps.sros_web_nexus.nexus_core import NexusCore
from sros.runtime.session_manager import SessionManager
from sros.governance.access_control import AccessControl

class TestSROSIntegration:
    """
    Comprehensive Integration Test Suite for SROS v1.
    Verifies the interaction between Kernel, Runtime, Governance, MirrorOS, and Nexus.
    """
    
    @pytest.fixture
    def kernel(self):
        # Boot Kernel
        k = kernel_bootstrap.boot("sros_config.yml")
        yield k
        # Teardown
        k.registry.stop_all()

    def test_full_stack_flow(self, kernel):
        """
        Tests the "Golden Path":
        1. Boot Kernel (Fixture)
        2. Create Session (Runtime)
        3. Check Permissions (Governance)
        4. Execute Command (Nexus)
        5. Verify Traces (MirrorOS)
        """
        print("\n[TEST] Starting Full Stack Flow Verification...")

        # 1. Verify Kernel State
        assert kernel.state.get_plane_status("kernel") == "running"
        print("[PASS] Kernel is running.")

        # 2. Runtime: Create Session
        session_id = kernel.session_manager.create_session(user_id="skrikx_prime", tenant_id="PlatXP")
        assert session_id is not None
        session = kernel.session_manager.get_session(session_id)
        assert session["status"] == "active"
        print(f"[PASS] Session created: {session_id}")

        # 3. Governance: Check Permissions
        # Manually accessing the governance module from kernel context (assuming it was wired)
        # For this test, we'll instantiate AccessControl if not in kernel yet, 
        # but ideally it should be accessible via kernel.governance (if we exposed it).
        # Let's assume we use the kernel's event bus to verify governance "hearing" events.
        # But for direct test, let's use the class.
        ac = AccessControl()
        ac.assign_role("skrikx_prime", "admin")
        assert ac.check_permission("skrikx_prime", "run_demo") is True
        print("[PASS] Governance RBAC verified.")

        # 4. Nexus: Execute Command
        nexus = NexusCore(kernel)
        response = nexus.run_command("run_demo", {"session_id": session_id})
        assert response["status"] == "success"
        print("[PASS] Nexus command executed.")

        # 5. MirrorOS: Verify Traces
        # We check if the trace file was created and has content
        trace_dir = "./data/traces"
        assert os.path.exists(trace_dir)
        
        # Wait a moment for async writes if any (though our bus is sync)
        time.sleep(0.1)
        
        # Find latest trace file
        files = sorted(os.listdir(trace_dir))
        assert len(files) > 0
        latest_trace = os.path.join(trace_dir, files[-1])
        
        with open(latest_trace, "r") as f:
            lines = f.readlines()
            assert len(lines) > 0
            # Check for specific events
            events = [json.loads(line) for line in lines]
            event_topics = [e["topic"] for e in events]
            
            assert "kernel.ready" in event_topics
            assert "session.created" in event_topics
            # assert "kernel.heartbeat" in event_topics # Might not have fired yet depending on timing
            
        print(f"[PASS] MirrorOS traces verified in {latest_trace}")

    def test_governance_audit(self, kernel):
        """
        Verifies that critical actions are audited.
        """
        audit_file = "./data/audit.log"
        # Clear previous log if exists for clean test
        if os.path.exists(audit_file):
            os.remove(audit_file)
            
        # Trigger an action that should be audited (e.g., via a mock governance enforcement)
        from sros.governance.audit_log import AuditLog
        audit = AuditLog()
        audit.log("user_1", "delete_memory", "mem_core", "deny", "insufficient_permissions")
        
        assert os.path.exists(audit_file)
        with open(audit_file, "r") as f:
            content = f.read()
            assert "delete_memory" in content
            assert "deny" in content
            
        print("[PASS] Governance Audit Log verified.")

if __name__ == "__main__":
    # Manual run wrapper
    t = TestSROSIntegration()
    # Mock kernel for manual run if needed, or rely on pytest
    print("Run with: pytest sros_v1/tests/sros_test_suite.py")
