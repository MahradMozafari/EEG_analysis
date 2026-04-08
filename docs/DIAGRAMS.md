# Diagrams

This folder contains both editable Mermaid diagrams and exported PNG files.

## Included diagrams

- `module_dependency_graph.mmd` / `.png`
- `function_call_graph.mmd` / `.png`
- `data_variable_flow_graph.mmd` / `.png`
- `pipeline_flow.mmd`

## Notes

- The **module dependency graph** comes from import-level relationships plus a few clearly-labeled inferred pipeline edges.
- The **function call graph** is based on static parsing of top-level functions and their detected local calls.
- The **data / variable flow graph** is intentionally conceptual. It documents how major artifacts move through the pipeline.

## Update process

1. Refactor the source files under `src/eeg_causal/`
2. Re-run `scripts/generate_call_graph.py`
3. Replace the PNG outputs if the structure changes significantly
4. Update `ARCHITECTURE.md` if ownership or stage boundaries change
