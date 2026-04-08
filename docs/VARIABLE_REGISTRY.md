# Variable Registry

This registry is meant to make future documentation easier by naming the major data artifacts that move through the pipeline.

## Core data artifacts

- `bids_root`: root path of the BIDS EEG dataset
- `subject_id` / `subj`: one subject key
- `roi_definition`: mapping from ROI names to channel names
- `roi_names`: ordered list of ROIs used in adjacency matrices
- `raw`: raw EEG object after loading
- `roi_data`: ROI-level time series after channel aggregation
- `epochs_data` / `windows`: segmented time-series slices used for causal estimation
- `candidates`: candidate grid of epoch-length / overlap settings
- `metadata`: windowing metadata such as start indices and ESS proxy
- `granger_adj`: Granger adjacency matrix
- `lingam_adj`: VAR-LiNGAM adjacency matrix
- `results`: subject-level serialized outputs
- `batch_results`: collection of subject outputs
- `group_networks`: aggregated group-level networks
- `params`: analysis parameter bundle

## Variable-flow summary

1. dataset paths are resolved
2. subject EEG is loaded
3. channels are aggregated into ROIs
4. ROI data is segmented into windows
5. windows are scored and/or used for causal discovery
6. connectivity matrices are saved as subject results
7. subject results are aggregated into group networks
8. group networks are visualized or featurized for classification
