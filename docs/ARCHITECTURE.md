# Architecture

## 1. System overview

The repository is organized around a staged EEG analysis pipeline:

1. **Environment validation**
2. **Configuration and path setup**
3. **Subject preprocessing**
4. **ROI aggregation**
5. **Auto-windowing / candidate evaluation**
6. **Directed connectivity estimation**
7. **Batch orchestration**
8. **Group-level aggregation**
9. **Visualization**
10. **Optional classification**

This is a good shape for GitHub because each stage can be documented, tested, and versioned independently.

## 2. Design principles

- Keep notebook experimentation separate from reusable library code.
- Split heavy computation from plotting and from file-export side effects.
- Make subject-level outputs serializable so group analysis is deterministic.
- Keep method choices explicit: Granger and VAR-LiNGAM should remain comparable.
- Treat window selection as a first-class design decision instead of a hidden constant.

## 3. Main layers

### Layer A — Configuration
Owns paths, default seeds, ROI dictionaries, and reproducibility settings.

### Layer B — Preprocessing
Loads EEG, optionally applies signal-space transforms, builds ROI-level signals, and creates epochs.

### Layer C — Window strategy
Evaluates candidate epoch lengths and overlaps using stationarity, fit quality, stability, and ESS-aware heuristics.

### Layer D — Causal discovery
Runs Granger causality and VAR-LiNGAM over prepared windows or epochs.

### Layer E — Batch execution
Loops over subjects, handles parallelism, and stores normalized results.

### Layer F — Aggregation and plots
Builds group summaries and network visualizations from saved results.

### Layer G — Downstream learning
Extracts graph-level features for classification or comparison experiments.

## 4. Recommended future cleanup

- Move all global prints into a logger.
- Eliminate duplicate code inherited from notebook cells.
- Add typed result containers for subject outputs.
- Add explicit schemas for saved JSON artifacts.
- Separate model selection metrics from visualization-ready summaries.
