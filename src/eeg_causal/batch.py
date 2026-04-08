from __future__ import annotations

import json
import multiprocessing
import os
from pathlib import Path
from typing import Dict, List, Tuple

from joblib import Parallel, delayed

from .preprocessing import preprocess_subject
from .causality import granger_causality_analysis, lingam_analysis


def process_single_subject(subj, bids_root, roi_def, roi_names, params, results_path, subj_groups):
    """
    Process one subject.
    
    Parameters
    ----------
    subj : str
        Subject ID
    bids_root : str
        BIDS path
    roi_def : dict
        ROI definitions
    roi_names : list
        ROI names
    params : dict
        Analysis parameters
    results_path : str
        Result output path
    subj_groups : dict
        Subject groups
    
    Returns
    -------
    result : dict or None
        Results, or None if an error occurs
    error : tuple or None
        (subject_id, error_message) on error
    """
    try:
        # Preprocess
        epochs_data = preprocess_subject(
            subj,
            bids_root,
            roi_def,
            epoch_length=params['epoch_length'],
            verbose=False
        )
        
        if len(epochs_data) < 5:  # At least 5 epochs are required
            return None, (subj, "insufficient epochs")
        
        # Granger
        granger_conn, granger_f = granger_causality_analysis(
            epochs_data,
            roi_names,
            max_lag=params['max_lag'],
            alpha=params['alpha_significance'],
            verbose=False
        )
        
        # LiNGAM
        lingam_conn = lingam_analysis(
            epochs_data,
            roi_names,
            lags=5,
            verbose=False
        )
        
        # Determine group
        group = None
        for g, subs in subj_groups.items():
            if subj in subs:
                group = g
                break
        
        # Save result
        result = {
            'subject_id': subj,
            'group': group,
            'n_epochs': len(epochs_data),
            'granger_connectivity': granger_conn.tolist(),
            'granger_f_values': granger_f.tolist(),
            'lingam_connectivity': lingam_conn.tolist(),
            'roi_names': roi_names
        }
        
        # Save individual file
        output_file = os.path.join(results_path, f"{subj}_causal_analysis.json")
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        return result, None
    
    except Exception as e:
        return None, (subj, str(e))





def run_batch(
    all_subjects: List[str],
    subject_groups: Dict[str, List[str]],
    bids_root: str,
    roi_definition: Dict[str, List[str]],
    roi_names: List[str],
    params: Dict,
    results_path: str,
    n_jobs: int | None = None,
):
    if n_jobs is None:
        n_jobs = max(1, multiprocessing.cpu_count() - 3)

    outputs = Parallel(n_jobs=n_jobs)(
        delayed(process_single_subject)(
            subj,
            bids_root,
            roi_definition,
            roi_names,
            params,
            results_path,
            subject_groups,
        )
        for subj in all_subjects
    )

    batch_results = [result for result, error in outputs if result is not None]
    failed_subjects = [error for result, error in outputs if error is not None]
    return batch_results, failed_subjects
