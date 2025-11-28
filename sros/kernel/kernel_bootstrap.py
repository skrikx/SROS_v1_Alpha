from .event_bus import EventBus
from .daemon_registry import DaemonRegistry
from .daemons.heartbeat_daemon import HeartbeatDaemon
from ..memory.memory_router import MemoryRouter

class KernelContext:
    def __init__(self, event_bus, memory, registry):
        self.event_bus = event_bus
        self.memory = memory
        self.registry = registry

def boot(config_path: str = "sros_config.yml") -> KernelContext:
    print(f"Booting SROS Kernel (config={config_path})...")
    
    # 1. Initialize Event Bus
    event_bus = EventBus()
    
    # 2. Initialize Memory
    memory = MemoryRouter()
    
    # 3. Initialize Registry
    registry = DaemonRegistry(event_bus)
    
    # 4. Register Core Daemons
    registry.register("heartbeat", HeartbeatDaemon(event_bus))
    
    # 5. Start Daemons
    registry.start_all()
    
    event_bus.publish("kernel", "kernel.ready", {})
    print("SROS Kernel Online.")
    import sys
    sys.stdout.flush()
    
    return KernelContext(event_bus, memory, registry)
