from __future__ import annotations

import json
from pathlib import Path

from .batch import run_batch
from .config import AnalysisParams, DEFAULT_ROI_DEFINITION, ProjectPaths, set_random_seed


def main(bids_root: str) -> None:
    paths = ProjectPaths.from_root(bids_root)
    paths.ensure()
    params = AnalysisParams()
    set_random_seed(params.random_seed)

    subject_groups_path = paths.bids_root / "subject_groups.json"
    with open(subject_groups_path, "r", encoding="utf-8") as f:
        subject_groups = json.load(f)

    all_subjects = subject_groups["AD"] + subject_groups["FTD"] + subject_groups["CN"]
    roi_names = list(DEFAULT_ROI_DEFINITION.keys())

    batch_results, failed_subjects = run_batch(
        all_subjects=all_subjects,
        subject_groups=subject_groups,
        bids_root=str(paths.bids_root),
        roi_definition=DEFAULT_ROI_DEFINITION,
        roi_names=roi_names,
        params=params.__dict__,
        results_path=str(paths.results_path),
    )

    print(f"Processed subjects: {len(batch_results)}")
    print(f"Failed subjects: {len(failed_subjects)}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run EEG causal analysis pipeline")
    parser.add_argument("--bids-root", required=True)
    args = parser.parse_args()
    main(args.bids_root)
