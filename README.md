# EEG Causal Connectivity Toolkit

A GitHub-ready repository scaffold for refactoring the original `granger_v5.ipynb` notebook into a maintainable Python package with documentation, diagrams, guide files, and contribution templates.

## What this repository contains

- A package-oriented source layout under `src/eeg_causal/`
- GitHub-friendly documentation under `docs/`
- Mermaid diagrams and exported PNG graphs under `docs/diagrams/`
- Basic packaging and contribution files for a public repository

## Project goal

This project studies EEG effective connectivity with a focus on:

- preprocessing subject-level EEG data
- aggregating channels into ROIs
- selecting sensible window / overlap settings
- estimating directed connectivity using **Granger causality** and **VAR-LiNGAM**
- aggregating subject results at the group level
- optionally extracting graph features for classification

## Why these methods are used

### Granger causality
Used to estimate directed predictive influence between ROI time series across epochs. A source ROI is considered informative for a target ROI when including its past values improves prediction beyond the target's own past.

### VAR-LiNGAM
Used as a second directed connectivity method to complement Granger causality. It assumes a linear non-Gaussian generative process and aims to recover a directed adjacency matrix for each epoch or subject-level segment.

### Auto-windowing
Used to choose practical epoch-length and overlap settings based on three priorities: stationarity, model fit quality, and split-half stability, with optional thinning and ESS estimates.

### ROI aggregation
Used to reduce raw channel-level EEG into anatomically meaningful regional signals before causal discovery.

### Group-level analysis
Used to average, summarize, and compare networks across diagnostic groups such as AD, FTD, and CN.

### Classification
Used as an optional downstream step to turn graph-derived features into discriminative representations for diagnosis-level experiments.

## Repository layout

```text
.
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── copilot-instructions.md
├── docs/
│   ├── api/
│   ├── guides/
│   ├── diagrams/
│   ├── ARCHITECTURE.md
│   ├── DIAGRAMS.md
│   ├── FILE_CONTRACTS.md
│   ├── FUNCTION_CATALOG.md
│   ├── METHODS.md
│   ├── NOTEBOOK_MIGRATION_GUIDE.md
│   └── VARIABLE_REGISTRY.md
├── scripts/
│   └── generate_call_graph.py
├── src/
│   └── eeg_causal/
├── tests/
├── AGENTS.md
├── CONTRIBUTING.md
├── LICENSE_TEMPLATE.md
├── MKDOCS_TEMPLATE.md
├── pyproject.toml
├── README.md
└── requirements.txt
```

## Package map

- `auto_windowing.py`: Epoch-length / overlap search, thinning, ESS estimation, and candidate scoring.
- `batch.py`: Parallelized subject-level execution and export of serialized analysis results.
- `causality.py`: Per-epoch connectivity estimation using Granger causality and VAR-LiNGAM.
- `classification.py`: Optional graph-feature extraction and ensemble-style classification utilities.
- `config.py`: Central parameters, paths, random seed, ROI definitions, and reproducibility defaults.
- `environment.py`: Dependency checks and runtime validation before the pipeline starts.
- `group_analysis.py`: Group aggregation, summary networks, and higher-level comparisons across cohorts.
- `helpers.py`: Shared signal-processing and statistical utilities used by preprocessing and causality layers.
- `main.py`: Top-level orchestration entrypoint that wires config and batch execution together.
- `preprocessing.py`: Subject-level EEG loading, ROI aggregation, optional CSD, and epoch creation.
- `visualization.py`: Heatmaps and graph visualizations for adjacency/connectivity matrices.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

## Documentation entry points

- `docs/ARCHITECTURE.md` — high-level design and pipeline story
- `docs/METHODS.md` — method-by-method explanation
- `docs/FILE_CONTRACTS.md` — file ownership, inputs, outputs, side effects
- `docs/FUNCTION_CATALOG.md` — extracted function list and intent
- `docs/VARIABLE_REGISTRY.md` — data artifacts and major variables
- `docs/DIAGRAMS.md` — all diagrams and how to update them
- `docs/guides/GITHUB_SETUP_GUIDE.md` — how to publish this repo cleanly
- `docs/guides/DOCS_WRITING_GUIDE.md` — how to continue documentation

## Important note

The source files were derived from notebook refactoring. Some implementation details still need cleanup before production release. The documentation here is designed to make that cleanup and future documentation much easier.


## Repository cleanup note

The Python source files in `src/eeg_causal/` were cleaned to remove remaining
placeholder text and to replace mixed-language comments with professional English
docstrings and comments, especially in `auto_windowing.py`.
