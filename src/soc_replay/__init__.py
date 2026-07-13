"""SOC_Replay: deterministic replay of synthetic defensive telemetry."""

from ._version import __version__
from .engine import ReplayResult, run_scenario

__all__ = ["ReplayResult", "run_scenario", "__version__"]
