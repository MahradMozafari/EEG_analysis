# GitHub Setup Guide

## 1. Initialize the repository

```bash
git init
git add .
git commit -m "Initial EEG causal connectivity scaffold"
```

## 2. Create the remote repository

- Create a new GitHub repository
- Push the code:

```bash
git remote add origin <YOUR_GITHUB_REPO_URL>
git branch -M main
git push -u origin main
```

## 3. Recommended repository settings

- Enable branch protection for `main`
- Require pull requests for major method changes
- Turn on Discussions if you want research-method debates
- Add repository topics such as:
  - eeg
  - neuroscience
  - granger-causality
  - lingam
  - time-series
  - python

## 4. First public-release checklist

- replace `LICENSE_TEMPLATE.md` with a chosen license
- verify dataset-sharing permissions
- remove large generated binary outputs if they belong in releases instead
- add a small demo dataset or mock test fixture
- publish a cleaner example notebook in `examples/`
