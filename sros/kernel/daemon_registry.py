from typing import Dict, Any

class DaemonRegistry:
    """
    Manages the lifecycle of Kernel Daemons.
    """
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.daemons: Dict[str, Any] = {}
        self.running: Dict[str, bool] = {}

    def register(self, name: str, daemon_instance: Any):
        self.daemons[name] = daemon_instance
        self.running[name] = False

    def start_all(self):
        print("Starting Kernel Daemons...")
        for name, daemon in self.daemons.items():
            try:
                if hasattr(daemon, 'start'):
                    daemon.start()
                self.running[name] = True
                self.event_bus.publish("kernel", "daemon.started", {"name": name})
                print(f"  [OK] {name}")
            except Exception as e:
                print(f"  [FAIL] {name}: {e}")

    def stop_all(self):
        print("Stopping Kernel Daemons...")
        for name, daemon in self.daemons.items():
            if self.running.get(name):
                if hasattr(daemon, 'stop'):
                    daemon.stop()
                self.running[name] = False
