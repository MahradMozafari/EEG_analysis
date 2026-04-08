from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List
import os
import numpy as np


DEFAULT_RANDOM_SEED = 42


@dataclass
class ProjectPaths:
    bids_root: Path
    processed_path: Path
    results_path: Path
    cache_dir: Path

    @classmethod
    def from_root(cls, bids_root: str | Path) -> "ProjectPaths":
        root = Path(bids_root)
        return cls(
            bids_root=root,
            processed_path=root / "processed",
            results_path=root / "results_causal",
            cache_dir=root / "cache",
        )

    def ensure(self) -> None:
        self.processed_path.mkdir(parents=True, exist_ok=True)
        self.results_path.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)


DEFAULT_ROI_DEFINITION: Dict[str, List[str]] = {
    "Frontal": ["Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8"],
    "Central": ["C3", "Cz", "C4"],
    "Temporal_L": ["T3", "T5"],
    "Temporal_R": ["T4", "T6"],
    "Parietal": ["P3", "Pz", "P4"],
    "Occipital": ["O1", "O2"],
}


@dataclass
class AnalysisParams:
    epoch_length: float = 4.0
    sampling_freq: int = 256
    max_lag: int = 10
    alpha_significance: float = 0.05
    overlap: float = 0.5
    random_seed: int = DEFAULT_RANDOM_SEED


def set_random_seed(seed: int = DEFAULT_RANDOM_SEED) -> None:
    np.random.seed(seed)
