import pytest
from sros.kernel import kernel_bootstrap
from sros.apps.sros_web_nexus.nexus_core import NexusCore

def test_nexus_demo_command():
    """
    Verifies that Nexus can trigger a demo command via the Kernel.
    """
    kernel = kernel_bootstrap.boot()
    nexus = NexusCore(kernel)
    
    result = nexus.run_command("run_demo")
    assert result["status"] == "success"
    
    kernel.registry.stop_all()
