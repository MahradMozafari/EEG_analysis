# CONTRIBUTING.md

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Contribution rules

- Keep commits focused.
- Add docs for every new public function.
- Add a test for every bug fix when possible.
- Do not introduce hidden randomness.
- If you change saved-output structure, document the migration path.

## Recommended branches

- `feature/...`
- `fix/...`
- `docs/...`
- `refactor/...`
