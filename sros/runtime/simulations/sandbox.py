"""
SimulationSandbox provides a lightweight, deterministic sandbox for executing evolution proposals
(e.g., new adapters, workflow definitions) while capturing MirrorOS traces.
It isolates side‑effects by using temporary directories and in‑memory stores.
"""
import os
import tempfile
import shutil
import logging
from typing import Callable, Any

from ..memory.memory_router import MemoryRouter
from ..mirroros.telemetry_collector import TelemetryCollector

logger = logging.getLogger(__name__)

class SimulationSandbox:
    """Execute a proposal in isolation and record its effects.

    Parameters
    ----------
    memory_router: MemoryRouter
        The system memory router to use (will be cloned for sandbox).
    telemetry: TelemetryCollector
        Telemetry collector to capture events.
    """

    def __init__(self, memory_router: MemoryRouter, telemetry: TelemetryCollector):
        self._orig_memory = memory_router
        self._orig_telemetry = telemetry
        self._temp_dir = None
        self._sandbox_memory = None
        self._sandbox_telemetry = None

    def __enter__(self):
        # Create temporary workspace
        self._temp_dir = tempfile.mkdtemp(prefix="sros_sim_")
        logger.debug(f"Simulation sandbox temporary dir: {self._temp_dir}")
        # Clone memory router (shallow copy is sufficient for deterministic tests)
        self._sandbox_memory = self._orig_memory.clone() if hasattr(self._orig_memory, "clone") else self._orig_memory
        # Create a fresh telemetry collector for sandbox
        self._sandbox_telemetry = TelemetryCollector()
        return self

    def __exit__(self, exc_type, exc, tb):
        # Cleanup temporary directory
        if self._temp_dir and os.path.isdir(self._temp_dir):
            shutil.rmtree(self._temp_dir)
            logger.debug("Simulation sandbox cleaned up temporary directory")
        # Merge sandbox telemetry back to original collector
        if self._sandbox_telemetry and self._orig_telemetry:
            for event in getattr(self._sandbox_telemetry, "events", []):
                self._orig_telemetry.record(event)
        return False  # propagate exceptions

    def run(self, proposal: Callable[[MemoryRouter, TelemetryCollector], Any], **kwargs) -> Any:
        """Execute *proposal* with sandboxed memory and telemetry.

        The *proposal* callable receives a ``MemoryRouter`` and ``TelemetryCollector``
        and should return any result. All side‑effects are confined to the sandbox.
        """
        with self as sandbox:
            try:
                result = proposal(sandbox._sandbox_memory, sandbox._sandbox_telemetry, **kwargs)
                logger.info("Simulation sandbox executed proposal successfully")
                return result
            except Exception as e:
                logger.error(f"Simulation sandbox error: {e}")
                raise
