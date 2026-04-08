# Function Catalog

This file enumerates the current top-level functions extracted from `src/eeg_causal/`.

## auto_windowing.py
Purpose: Epoch-length / overlap search, thinning, ESS estimation, and candidate scoring.

### Classes
- `WindowMetadata`

### Functions
- `validate_windowing_params(epoch_length_sec, overlap, sfreq, data_shape)`
- `build_candidate_grid(epoch_lengths, overlaps, include_baseline)`
- `create_windows_from_data(data, sfreq, epoch_length_sec, overlap, apply_hann, max_windows, sampling_mode, min_distance, random_seed, return_metadata)`
- `thinning_indices(n_windows, overlap)`
- `thin_windows(windows, overlap)`
- `estimate_ess(n_windows, overlap, method, windows, feature_func)`
- `compute_stationarity_score(windows, alpha)`
- `compute_fit_quality_score(windows, lag)`
- `compute_simple_connectivity(windows, threshold)`
- `compute_stability_score(windows, n_splits, threshold)`
- `evaluate_candidate(data, sfreq, epoch_length_sec, overlap, max_windows, apply_thinning, ess_method, sampling_mode, random_seed, verbose)`
- `run_stability_sweep(data, sfreq, candidates, max_windows, sampling_mode, apply_thinning, ess_method, random_seed, verbose)`
- `select_by_constraint_first(df, stationarity_min, fit_quality_min)`
- `select_by_pareto_knee(df)`
- `select_by_rank_aggregation(df)`
- `select_by_entropy_weighting(df)`

## batch.py
Purpose: Parallelized subject-level execution and export of serialized analysis results.

### Functions
- `process_single_subject(subj, bids_root, roi_def, roi_names, params, results_path, subj_groups)`
- `run_batch(all_subjects, subject_groups, bids_root, roi_definition, roi_names, params, results_path, n_jobs)`

## causality.py
Purpose: Per-epoch connectivity estimation using Granger causality and VAR-LiNGAM.

### Functions
- `granger_causality_analysis(epochs_data, roi_names, max_lag, alpha, verbose)`
- `lingam_analysis(epochs_data, roi_names, lags, verbose)`

## classification.py
Purpose: Optional graph-feature extraction and ensemble-style classification utilities.

### Classes
- `BrainNetworkEnsemble`

### Functions
- `extract_graph_features(granger_adj, lingam_adj)`

## config.py
Purpose: Central parameters, paths, random seed, ROI definitions, and reproducibility defaults.

### Classes
- `ProjectPaths`
- `AnalysisParams`

### Functions
- `set_random_seed(seed)`

## environment.py
Purpose: Dependency checks and runtime validation before the pipeline starts.

### Classes
- `EnvironmentReport`

### Functions
- `safe_import(name)`
- `check_environment(required, optional)`

## group_analysis.py
Purpose: Group aggregation, summary networks, and higher-level comparisons across cohorts.

### Functions
- `compute_group_network(results, group_name, method)`
- `build_group_networks(batch_results, roi_names, results_path)`

## helpers.py
Purpose: Shared signal-processing and statistical utilities used by preprocessing and causality layers.

### Functions
- `check_stationarity(data, alpha)`
- `aggregate_channels_to_roi(raw, roi_definition, method)`
- `select_optimal_lag(data, max_lag, min_lag)`

## main.py
Purpose: Top-level orchestration entrypoint that wires config and batch execution together.

### Functions
- `main(bids_root)`

## preprocessing.py
Purpose: Subject-level EEG loading, ROI aggregation, optional CSD, and epoch creation.

### Functions
- `preprocess_subject(subject_id, bids_root, roi_definition, epoch_length, verbose)`

## visualization.py
Purpose: Heatmaps and graph visualizations for adjacency/connectivity matrices.

### Functions
- `plot_connectivity_matrix(connectivity, roi_names, title, threshold, save_path)`
- `plot_network_graph(connectivity, roi_names, title, threshold, save_path)`
