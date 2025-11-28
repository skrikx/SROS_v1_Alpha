import time
import threading

class HeartbeatDaemon:
    """
    Emits a heartbeat event every N seconds.
    """
    def __init__(self, event_bus, interval=1.0):
        self.event_bus = event_bus
        self.interval = interval
        self.running = False
        self._thread = None

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    def _loop(self):
        while self.running:
            self.event_bus.publish("kernel", "kernel.heartbeat", {"status": "alive"})
            time.sleep(self.interval)
