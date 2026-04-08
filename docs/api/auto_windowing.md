# API: auto_windowing.py

**Purpose**: Epoch-length / overlap search, thinning, ESS estimation, and candidate scoring.

## Classes

- `WindowMetadata`

## Functions

### `validate_windowing_params(epoch_length_sec, overlap, sfreq, data_shape)`

- Inputs: document explicitly during cleanup
- Outputs: document explicitly during cleanup
- Notes: extracted from the current scaffold

### `build_candidate_grid(epoch_lengths, overlaps, include_baseline)`

- Inputs: document explicitly during cleanup
- Outputs: document explicitly during cleanup
- Notes: extracted from the current scaffold

### `create_windows_from_data(data, sfreq, epoch_length_sec, overlap, apply_hann, max_windows, sampling_mode, min_distance, random_seed, return_metadata)`

- Inputs: document explicitly during cleanup
- Outputs: document explicitly during cleanup
- Notes: extracted from the current scaffold

### `thinning_indices(n_windows, overlap)`

- Inputs: document explicitly during cleanup
- Outputs: document explicitly during cleanup
- Notes: extracted from the current scaffold

### `thin_windows(windows, overlap)`

- Inputs: document explicitly during cleanup
- Outputs: document explicitly during cleanup
- Notes: extracted from the current scaffold

### `estimate_ess(n_windows, overlap, method, windows, feature_func)`

- Inputs: document explicitly during cleanup
- Outputs: document explicitly during cleanup
- Notes: extracted from the current scaffold

### `compute_stationarity_score(windows, alpha)`

- Inputs: document explicitly during cleanup
- Outputs: document explicitly during cleanup
- Notes: extracted from the current scaffold

### `compute_fit_quality_score(windows, lag)`

- Inputs: document explicitly during cleanup
- Outputs: document explicitly during cleanup
- Notes: extracted from the current scaffold

### `compute_simple_connectivity(windows, threshold)`

- Inputs: document explicitly during cleanup
- Outputs: document explicitly during cleanup
- Notes: extracted from the current scaffold

### `compute_stability_score(windows, n_splits, threshold)`

- Inputs: document explicitly during cleanup
- Outputs: document explicitly during cleanup
- Notes: extracted from the current scaffold

### `evaluate_candidate(data, sfreq, epoch_length_sec, overlap, max_windows, apply_thinning, ess_method, sampling_mode, random_seed, verbose)`

- Inputs: document explicitly during cleanup
- Outputs: document explicitly during cleanup
- Notes: extracted from the current scaffold

### `run_stability_sweep(data, sfreq, candidates, max_windows, sampling_mode, apply_thinning, ess_method, random_seed, verbose)`

- Inputs: document explicitly during cleanup
- Outputs: document explicitly during cleanup
- Notes: extracted from the current scaffold

### `select_by_constraint_first(df, stationarity_min, fit_quality_min)`

- Inputs: document explicitly during cleanup
- Outputs: document explicitly during cleanup
- Notes: extracted from the current scaffold

### `select_by_pareto_knee(df)`

- Inputs: document explicitly during cleanup
- Outputs: document explicitly during cleanup
- Notes: extracted from the current scaffold

### `select_by_rank_aggregation(df)`

- Inputs: document explicitly during cleanup
- Outputs: document explicitly during cleanup
- Notes: extracted from the current scaffold

### `select_by_entropy_weighting(df)`

- Inputs: document explicitly during cleanup
- Outputs: document explicitly during cleanup
- Notes: extracted from the current scaffold
