from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from .visualization import plot_connectivity_matrix, plot_network_graph

# =======================
# Group-level analysis
# =======================

def compute_group_network(results, group_name, method='granger'):
    """
    Compute average connectivity for a group
    """
    group_results = [r for r in results if r['group'] == group_name]
    
    if len(group_results) == 0:
        return None, 0
    
    connectivity_sum = None
    
    for r in group_results:
        conn = np.array(r[f'{method}_connectivity'])
        
        if connectivity_sum is None:
            connectivity_sum = conn
        else:
            connectivity_sum += conn
    
    avg_connectivity = connectivity_sum / len(group_results)
    
    return avg_connectivity, len(group_results)


def build_group_networks(batch_results, roi_names, results_path):
    group_networks = {}
    for method in ["granger", "lingam"]:
        group_networks[method] = {}
        for group_name in ["AD", "FTD", "CN"]:
            avg_conn, n_subj = compute_group_network(batch_results, group_name, method=method)
            if avg_conn is None:
                continue
            group_networks[method][group_name] = avg_conn
            output_file = os.path.join(results_path, f"group_{group_name}_{method}.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump({
                    "group": group_name,
                    "method": method,
                    "n_subjects": n_subj,
                    "connectivity": avg_conn.tolist(),
                    "roi_names": roi_names,
                }, f, indent=2)
    return group_networks
