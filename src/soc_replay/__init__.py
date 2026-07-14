"""SOC_Replay: deterministic defensive telemetry evidence pipeline."""

from ._version import __version__
from .engine import ReplayResult, run_scenario
from .pipeline import PipelineConfig, ReplayPipeline
from .proofs import IndexEquivalenceProof, prove_index_equivalence

__all__ = [
    "IndexEquivalenceProof",
    "PipelineConfig",
    "ReplayPipeline",
    "ReplayResult",
    "__version__",
    "prove_index_equivalence",
    "run_scenario",
]
