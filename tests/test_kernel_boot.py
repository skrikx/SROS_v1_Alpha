import pytest
from sros.kernel import kernel_bootstrap

def test_kernel_boot():
    """
    Verifies that the kernel boots and returns a context.
    """
    kernel = kernel_bootstrap.boot()
    assert kernel is not None
    assert kernel.event_bus is not None
    assert kernel.memory is not None
    assert kernel.registry is not None
    
    # Clean up (stop daemons)
    kernel.registry.stop_all()
