# Methods

## Overview

This project combines signal preprocessing, window-selection heuristics, and directed connectivity methods.

## 1. ROI aggregation

Used to reduce raw channel-level EEG into anatomically meaningful regional signals before causal discovery.

Typical input:
- raw or preprocessed EEG channels
- ROI channel definitions
- aggregation method such as mean

Typical output:
- `roi_data`: array-like regional time series
- `roi_names`: ordered ROI labels

## 2. Auto-windowing

Used to choose practical epoch-length and overlap settings based on three priorities: stationarity, model fit quality, and split-half stability, with optional thinning and ESS estimates.

The auto-windowing logic uses several ideas:

- **candidate grid**: tries multiple epoch lengths and overlaps
- **thinning**: reduces dependence caused by overlapping windows
- **ESS proxy**: estimates how much effective information remains
- **stationarity score**: rewards windows that better satisfy time-series assumptions
- **fit quality score**: checks whether the local VAR fit is reasonable
- **stability score**: checks whether estimated connectivity is reasonably reproducible

Selection strategies present in the scaffold:
- constraint-first filtering
- Pareto + knee selection
- rank aggregation
- entropy weighting

## 3. Granger causality

Used to estimate directed predictive influence between ROI time series across epochs. A source ROI is considered informative for a target ROI when including its past values improves prediction beyond the target's own past.

Why it is useful here:
- it matches the temporal-prediction logic of multivariate EEG time series
- it provides directed edges
- it is widely interpretable in neuroscience pipelines

Main caveats:
- sensitive to lag choice
- assumes a suitable degree of stationarity
- can be affected by volume conduction and preprocessing choices

## 4. VAR-LiNGAM

Used as a second directed connectivity method to complement Granger causality. It assumes a linear non-Gaussian generative process and aims to recover a directed adjacency matrix for each epoch or subject-level segment.

Why it is included:
- provides a second directed method with different assumptions
- useful as a methodological comparison against Granger
- may capture patterns missed by purely predictive causality measures

Main caveats:
- depends on linearity / non-Gaussian assumptions
- can be unstable when sample size is small
- benefits from careful epoch selection and ROI design

## 5. Group-level analysis

Used to average, summarize, and compare networks across diagnostic groups such as AD, FTD, and CN.

Typical group outputs:
- average connectivity matrices
- thresholded connectivity graphs
- diagnostic-group summaries
- saved plots for papers or reports

## 6. Classification

Used as an optional downstream step to turn graph-derived features into discriminative representations for diagnosis-level experiments.

Typical role:
- graph features from Granger and LiNGAM matrices become inputs for a diagnostic model
- useful for comparing interpretability-focused causal analysis with downstream predictive performance
