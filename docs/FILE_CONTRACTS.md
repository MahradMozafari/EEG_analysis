# File Contracts

Each file should own a clear responsibility, inputs, outputs, and side effects.

## auto_windowing.py
**Responsibility**: Epoch-length / overlap search, thinning, ESS estimation, and candidate scoring.

**Expected inputs**:
- `apply_hann`
- `data`
- `data_shape`
- `epoch_length_sec`
- `epoch_lengths`
- `include_baseline`
- `max_windows`
- `min_distance`
- `n_windows`
- `overlap`
- `overlaps`
- `random_seed`
- `return_metadata`
- `sampling_mode`
- `sfreq`

**Expected outputs**:
- module-specific intermediate artifacts or final outputs

**Side effects**:
- Should ideally remain side-effect light

---

## batch.py
**Responsibility**: Parallelized subject-level execution and export of serialized analysis results.

**Expected inputs**:
- `all_subjects`
- `bids_root`
- `n_jobs`
- `params`
- `results_path`
- `roi_def`
- `roi_definition`
- `roi_names`
- `subj`
- `subj_groups`
- `subject_groups`

**Expected outputs**:
- per-subject serialized results
- aggregate execution summary

**Side effects**:
- May save files to disk
- May print or log progress

---

## causality.py
**Responsibility**: Per-epoch connectivity estimation using Granger causality and VAR-LiNGAM.

**Expected inputs**:
- `alpha`
- `epochs_data`
- `lags`
- `max_lag`
- `roi_names`
- `verbose`

**Expected outputs**:
- directed adjacency / connectivity matrices
- p-values or model-fit metadata
- subject-level method outputs

**Side effects**:
- Should ideally remain side-effect light

---

## classification.py
**Responsibility**: Optional graph-feature extraction and ensemble-style classification utilities.

**Expected inputs**:
- `granger_adj`
- `lingam_adj`

**Expected outputs**:
- module-specific intermediate artifacts or final outputs

**Side effects**:
- Should ideally remain side-effect light

---

## config.py
**Responsibility**: Central parameters, paths, random seed, ROI definitions, and reproducibility defaults.

**Expected inputs**:
- `seed`

**Expected outputs**:
- module-specific intermediate artifacts or final outputs

**Side effects**:
- Should ideally remain side-effect light

---

## environment.py
**Responsibility**: Dependency checks and runtime validation before the pipeline starts.

**Expected inputs**:
- `name`
- `optional`
- `required`

**Expected outputs**:
- module-specific intermediate artifacts or final outputs

**Side effects**:
- Should ideally remain side-effect light

---

## group_analysis.py
**Responsibility**: Group aggregation, summary networks, and higher-level comparisons across cohorts.

**Expected inputs**:
- `batch_results`
- `group_name`
- `method`
- `results`
- `results_path`
- `roi_names`

**Expected outputs**:
- group-average networks
- plots or exported matrices

**Side effects**:
- May save files to disk
- May print or log progress

---

## helpers.py
**Responsibility**: Shared signal-processing and statistical utilities used by preprocessing and causality layers.

**Expected inputs**:
- `alpha`
- `data`
- `max_lag`
- `method`
- `min_lag`
- `raw`
- `roi_definition`

**Expected outputs**:
- module-specific intermediate artifacts or final outputs

**Side effects**:
- Should ideally remain side-effect light

---

## main.py
**Responsibility**: Top-level orchestration entrypoint that wires config and batch execution together.

**Expected inputs**:
- `bids_root`

**Expected outputs**:
- module-specific intermediate artifacts or final outputs

**Side effects**:
- May save files to disk
- May print or log progress

---

## preprocessing.py
**Responsibility**: Subject-level EEG loading, ROI aggregation, optional CSD, and epoch creation.

**Expected inputs**:
- `bids_root`
- `epoch_length`
- `roi_definition`
- `subject_id`
- `verbose`

**Expected outputs**:
- ROI time series or epoch-ready subject data
- subject metadata
- optional preprocessing diagnostics

**Side effects**:
- Should ideally remain side-effect light

---

## visualization.py
**Responsibility**: Heatmaps and graph visualizations for adjacency/connectivity matrices.

**Expected inputs**:
- `connectivity`
- `roi_names`
- `save_path`
- `threshold`
- `title`

**Expected outputs**:
- module-specific intermediate artifacts or final outputs

**Side effects**:
- May save files to disk
- May print or log progress

---
