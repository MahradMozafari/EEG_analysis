from __future__ import annotations

import os
from typing import Dict, List
import numpy as np
import mne

from .helpers import aggregate_channels_to_roi, check_stationarity

def preprocess_subject(subject_id, bids_root, roi_definition, epoch_length=4, verbose=True):
    """
    Complete preprocessing pipeline for one subject
    
    Parameters:
    -----------
    subject_id : str
        Subject ID (e.g., 'sub-001')
    bids_root : str
        Path to BIDS root
    roi_definition : dict
        ROI definition
    epoch_length : float
        Epoch length in seconds
    verbose : bool
        Print progress
    
    Returns:
    --------
    epochs_data : list of ndarray
        List of ROI time series, each shape (n_roi, n_samples)
    """
    # 1. Load data
    fif_path = os.path.join(bids_root, "processed", f"{subject_id}_raw.fif")
    
    if not os.path.exists(fif_path):
        if verbose:
            print(f"⚠️ {subject_id}: file does not exist")
        return []
    
    try:
        raw = mne.io.read_raw_fif(fif_path, preload=True, verbose=False)
    except Exception as e:
        if verbose:
            print(f"❌ {subject_id}: error while loading file - {e}")
        return []
    
    # 2. CSD Transform
    try:
        from mne.preprocessing import compute_current_source_density
        
        # CSD requires a montage
        if raw.get_montage() is None:
            montage = mne.channels.make_standard_montage('standard_1020')
            raw.set_montage(montage, on_missing='ignore')
        
        raw_csd = compute_current_source_density(raw)
        if verbose:
            print(f"   ✅ CSD transform applied")
    except Exception as e:
        if verbose:
            print(f"   ⚠️ CSD failed ({str(e)}), using raw data")
        raw_csd = raw
    
    # 3. ROI aggregation
    try:
        roi_data = aggregate_channels_to_roi(raw_csd, roi_definition)
    except Exception as e:
        if verbose:
            print(f"❌ {subject_id}: ROI aggregation failed - {e}")
        return []
    
    # 4. Epoching
    sfreq = raw.info['sfreq']
    epoch_samples = int(epoch_length * sfreq)
    n_samples = roi_data.shape[1]
    n_epochs = n_samples // epoch_samples
    
    epochs_data = []
    stationary_count = 0
    
    for i in range(n_epochs):
        start = i * epoch_samples
        end = start + epoch_samples
        epoch = roi_data[:, start:end]
        
        # 5. Stationarity check
        if check_stationarity(epoch):
            epochs_data.append(epoch)
            stationary_count += 1
    
    if verbose:
        print(f"✅ {subject_id}: {stationary_count}/{n_epochs} epochs (stationary)")
    
    return epochs_data


print("✅ Preprocessing pipeline defined")
