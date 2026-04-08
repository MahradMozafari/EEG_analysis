from __future__ import annotations

import importlib
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

OPTIONAL_IMPORTS = {
    "torch": "GNN classification",
    "torch_geometric": "graph neural networks",
    "pyriemann": "riemannian classification",
    "dask": "distributed/parallel processing",
}


@dataclass
class EnvironmentReport:
    available: Dict[str, bool]
    missing_required: List[str]
    missing_optional: List[str]


def safe_import(name: str) -> bool:
    try:
        importlib.import_module(name)
        return True
    except Exception:
        return False


def check_environment(required: List[str], optional: List[str] | None = None) -> EnvironmentReport:
    optional = optional or []
    available: Dict[str, bool] = {}
    missing_required: List[str] = []
    missing_optional: List[str] = []

    for name in required:
        ok = safe_import(name)
        available[name] = ok
        if not ok:
            missing_required.append(name)

    for name in optional:
        ok = safe_import(name)
        available[name] = ok
        if not ok:
            missing_optional.append(name)

    warnings.filterwarnings("ignore")
    return EnvironmentReport(available, missing_required, missing_optional)
