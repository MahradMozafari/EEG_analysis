from __future__ import annotations

import numpy as np
from tqdm import tqdm
from lingam import VARLiNGAM
from statsmodels.tsa.stattools import grangercausalitytests

from .helpers import select_optimal_lag

def granger_causality_analysis(epochs_data, roi_names, max_lag=10, alpha=0.05, verbose=True):
    """
    Perform Granger causality analysis on epochs
    
    Parameters:
    -----------
    epochs_data : list of ndarray
        List of epochs, each shape (n_roi, n_samples)
    roi_names : list
        List of ROI names
    max_lag : int
        Maximum lag to test
    alpha : float
        Significance level
    verbose : bool
        Show progress
    
    Returns:
    --------
    connectivity : ndarray, shape (n_roi, n_roi)
        Connectivity matrix (proportion of significant epochs)
    f_values : ndarray, shape (n_roi, n_roi)
        Average F-statistic values
    """
    n_roi = len(roi_names)
    n_epochs = len(epochs_data)
    
    if n_epochs == 0:
        return np.zeros((n_roi, n_roi)), np.zeros((n_roi, n_roi))
    
    # Initialize
    connectivity_counts = np.zeros((n_roi, n_roi))
    f_values_sum = np.zeros((n_roi, n_roi))
    test_counts = np.zeros((n_roi, n_roi))  # Used to average F-values
    
    iterator = tqdm(epochs_data, desc="Granger") if verbose else epochs_data
    
    for epoch in iterator:
        # Transpose for statsmodels (needs shape: n_samples, n_roi)
        data_t = epoch.T
        
        # Check that enough samples are available
        if data_t.shape[0] < max_lag * 2:
            continue
        
        # Select optimal lag for this epoch
        lag = select_optimal_lag(data_t, max_lag=max_lag)
        
        # Test all pairwise connections
        for i in range(n_roi):
            for j in range(n_roi):
                if i != j:
                    # Test if i -> j (i causes j)
                    test_data = data_t[:, [j, i]]  # [target, source]
                    
                    try:
                        result = grangercausalitytests(
                            test_data, 
                            maxlag=lag, 
                            verbose=False
                        )
                        
                        # Get p-value and F-value from F-test at optimal lag
                        p_value = result[lag][0]['ssr_ftest'][1]
                        f_value = result[lag][0]['ssr_ftest'][0]
                        
                        f_values_sum[i, j] += f_value
                        test_counts[i, j] += 1
                        
                        if p_value < alpha:
                            connectivity_counts[i, j] += 1
                    except Exception as e:
                        # Debug: uncomment to inspect errors
                        # print(f"Granger test failed for {roi_names[i]}->{roi_names[j]}: {e}")
                        continue
    
    # Normalize by number of epochs
    connectivity = connectivity_counts / n_epochs
    
    # Average F-values
    f_values = np.divide(f_values_sum, test_counts, 
                         out=np.zeros_like(f_values_sum), 
                         where=test_counts>0)
    
    return connectivity, f_values


print("✅ Granger function defined")

def lingam_analysis(epochs_data, roi_names, lags=5, verbose=True):
    """
    Perform VAR-LiNGAM analysis on epochs
    
    Parameters:
    -----------
    epochs_data : list of ndarray
        List of epochs, each shape (n_roi, n_samples)
    roi_names : list
        List of ROI names
    lags : int
        Number of lags
    verbose : bool
        Show progress
    
    Returns:
    --------
    connectivity : ndarray, shape (n_roi, n_roi)
        Connectivity matrix (mean absolute causal effect)
    """
    n_roi = len(roi_names)
    n_epochs = len(epochs_data)
    
    if n_epochs == 0:
        return np.zeros((n_roi, n_roi))
    
    connectivity_sum = np.zeros((n_roi, n_roi))
    valid_epochs = 0
    
    iterator = tqdm(epochs_data, desc="LiNGAM") if verbose else epochs_data
    
    for epoch in iterator:
        # Transpose for LiNGAM (needs shape: n_samples, n_roi)
        data_t = epoch.T
        
        # Check that enough samples are available
        if data_t.shape[0] < lags * 10:
            continue
        
        try:
            # Fit VAR-LiNGAM
            model = VARLiNGAM(lags=lags, prune=False)
            model.fit(data_t)
            
            # Sum effects across all lags
            # adjacency_matrices_ = [B(0), B(1), ..., B(lags)]
            # B(0) = instantaneous, B(τ) = lagged effects
            
            total_effect = np.zeros((n_roi, n_roi))
            
            for lag_idx, B_lag in enumerate(model.adjacency_matrices_):
                # Sum the absolute causal-effect magnitudes
                total_effect += np.abs(B_lag)
            
            # Normalize by number of lag matrices
            if len(model.adjacency_matrices_) > 0:
                total_effect /= len(model.adjacency_matrices_)
            
            connectivity_sum += total_effect
            valid_epochs += 1
            
        except Exception as e:
            # Debug: uncomment to inspect errors
            # print(f"LiNGAM failed: {e}")
            continue
    
    if valid_epochs == 0:
        return np.zeros((n_roi, n_roi))
    
    # Average over epochs
    connectivity = connectivity_sum / valid_epochs
    
    if verbose:
        print(f"   Valid epochs for LiNGAM: {valid_epochs}/{n_epochs}")
    
    return connectivity


print("✅ LiNGAM function defined")
