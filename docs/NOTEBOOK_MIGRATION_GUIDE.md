# Notebook Migration Guide

## Goal

Move from a monolithic notebook into a package that is easier to test, document, and publish.

## Recommended migration order

1. Stabilize `config.py`
2. Stabilize `helpers.py`
3. Stabilize `preprocessing.py`
4. Stabilize `auto_windowing.py`
5. Stabilize `causality.py`
6. Stabilize `batch.py`
7. Stabilize `group_analysis.py`
8. Stabilize `visualization.py`
9. Treat `classification.py` as optional until core analysis is reproducible

## Refactoring rules

- One function should do one job.
- Separate pure computation from save / print / plot side effects.
- Avoid notebook-style global execution at import time.
- Replace ad hoc dictionaries with typed dataclasses where useful.
- Make every saved artifact reproducible from a config + subject list.

## Suggested tests to add first

- candidate-grid validation
- thinning and ESS behavior
- lag-selection sanity checks
- shape consistency of ROI aggregation
- connectivity matrix dimensionality
- subject-result serialization
