from __future__ import annotations

import numpy as np
from statsmodels.tsa.stattools import adfuller, kpss

def check_stationarity(data, alpha=0.05):
    """
    Check stationarity using Augmented Dickey-Fuller test
    
    Parameters:
    -----------
    data : ndarray, shape (n_roi, n_samples)
        Time series data
    alpha : float
        Significance level
    
    Returns:
    --------
    is_stationary : bool
        True if all ROIs are stationary
    """
    n_roi = data.shape[0]
    
    for i in range(n_roi):
        try:
            result = adfuller(data[i])
            p_value = result[1]
            
            if p_value > alpha:
                return False  # Not stationary
        except:
            return False  # On failure, assume the signal is non-stationary
    
    return True  # All ROIs are stationary


def aggregate_channels_to_roi(raw, roi_definition, method='mean'):
    """
    Aggregate EEG channels into ROIs
    
    Parameters:
    -----------
    raw : mne.io.Raw
        Raw EEG data
    roi_definition : dict
        Dictionary mapping ROI names to channel lists
    method : str
        'mean' or 'pca'
    
    Returns:
    --------
    roi_data : ndarray, shape (n_roi, n_samples)
        ROI time series
    """
    data = raw.get_data()
    ch_names = raw.ch_names
    n_samples = data.shape[1]
    n_roi = len(roi_definition)
    
    roi_data = np.zeros((n_roi, n_samples))
    
    for roi_idx, (roi_name, channels) in enumerate(roi_definition.items()):
        # Robust channel-index lookup (case-insensitive)
        ch_indices = []
        for ch in channels:
            # Try exact match first
            if ch in ch_names:
                ch_indices.append(ch_names.index(ch))
            else:
                # Try case-insensitive
                ch_upper = ch.upper()
                for idx, ch_name in enumerate(ch_names):
                    if ch_name.upper() == ch_upper:
                        ch_indices.append(idx)
                        break
        
        if len(ch_indices) == 0:
            print(f"⚠️ Warning: No channels found for ROI {roi_name}")
            # Continue with zeros instead of raising an exception
            roi_data[roi_idx] = np.zeros(n_samples)
            continue
        
        # Aggregate
        roi_channels = data[ch_indices, :]
        
        if method == 'mean':
            roi_data[roi_idx] = np.mean(roi_channels, axis=0)
        elif method == 'pca':
            from sklearn.decomposition import PCA
            pca = PCA(n_components=1)
            roi_data[roi_idx] = pca.fit_transform(roi_channels.T).flatten()
    
    return roi_data


def select_optimal_lag(data, max_lag=10, min_lag=1):
    """
    Select optimal lag using BIC
    
    Parameters:
    -----------
    data : ndarray, shape (n_samples, n_roi)
        ROI time series (transposed)
    max_lag : int
        Maximum lag to test
    min_lag : int
        Minimum lag to test
    
    Returns:
    --------
    optimal_lag : int
        Best lag according to BIC
    """
    # Check that enough samples are available
    n_samples = data.shape[0]
    max_possible_lag = n_samples // 10  # At least 10 samples per lag
    max_lag = min(max_lag, max_possible_lag)
    
    if max_lag < min_lag:
        return min_lag
    
    try:
        model = VAR(data)
        bic_values = {}
        
        for p in range(min_lag, max_lag + 1):
            try:
                result = model.fit(p, verbose=False)
                bic_values[p] = result.bic
            except:
                continue
        
        if len(bic_values) == 0:
            return min_lag  # Default
        
        optimal_lag = min(bic_values, key=bic_values.get)
        return optimal_lag
    except:
        return min_lag


print("✅ Helper functions defined")
