from __future__ import annotations

"""Utilities for window generation, thinning, ESS estimation, and candidate scoring.

This module supports the EEG causal-analysis pipeline by creating candidate window
configurations, extracting windows from ROI time series, estimating dependence-aware
sample counts, and ranking candidate `(epoch_length_sec, overlap)` pairs.

The implementation is intentionally lightweight and notebook-friendly, but the public
functions are written so they can be documented and tested as reusable library code.
"""

import warnings
from dataclasses import dataclass
from typing import Callable, Dict, List, Literal, Optional, Tuple

import numpy as np
import pandas as pd
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller
from tqdm import tqdm


# ---------------------------------------------------------------------------
# Candidate grid
# ---------------------------------------------------------------------------

def validate_windowing_params(
    epoch_length_sec: float,
    overlap: float,
    sfreq: float,
    data_shape: Optional[Tuple[int, int]] = None,
) -> None:
    """Validate the main windowing parameters.

    Parameters
    ----------
    epoch_length_sec
        Window length in seconds.
    overlap
        Fractional overlap between consecutive windows. Must satisfy
        ``0 <= overlap < 1``.
    sfreq
        Sampling frequency in Hz.
    data_shape
        Optional tuple ``(n_channels, n_samples)`` used to verify that the
        requested window can fit inside the provided time series.

    Raises
    ------
    ValueError
        If any parameter is outside the valid range.
    """
    if epoch_length_sec <= 0:
        raise ValueError(f"epoch_length_sec must be positive, got {epoch_length_sec}.")

    if not (0 <= overlap < 1.0):
        raise ValueError(f"overlap must be in [0, 1), got {overlap}.")

    if overlap >= 0.99:
        warnings.warn(
            f"overlap={overlap} is extremely high; adjacent windows will be highly dependent.",
            UserWarning,
        )

    if sfreq <= 0:
        raise ValueError(f"sfreq must be positive, got {sfreq}.")

    if data_shape is not None:
        _, n_samples = data_shape
        window_samples = int(epoch_length_sec * sfreq)
        if window_samples > n_samples:
            raise ValueError(
                f"Requested window has {window_samples} samples, but the signal only "
                f"contains {n_samples} samples."
            )


def build_candidate_grid(
    epoch_lengths: List[float],
    overlaps: List[float],
    include_baseline: bool = True,
) -> List[Dict[str, float]]:
    """Build a sorted candidate grid of window lengths and overlap values.

    Parameters
    ----------
    epoch_lengths
        Candidate epoch lengths in seconds.
    overlaps
        Candidate overlap fractions.
    include_baseline
        If ``True``, force the grid to include an overlap value of ``0.0`` as a
        non-overlapping baseline condition.

    Returns
    -------
    list of dict
        Each candidate has the form
        ``{"epoch_length_sec": float, "overlap": float}``.
    """
    for length in epoch_lengths:
        if length <= 0:
            raise ValueError(
                f"All candidate epoch lengths must be positive. Found {length}."
            )

    for overlap in overlaps:
        if not (0 <= overlap < 1.0):
            raise ValueError(f"overlap must be in [0, 1), got {overlap}.")

    unique_overlaps = set(overlaps)
    if include_baseline and 0.0 not in unique_overlaps:
        unique_overlaps.add(0.0)

    return [
        {"epoch_length_sec": length, "overlap": overlap}
        for length in sorted(epoch_lengths)
        for overlap in sorted(unique_overlaps)
    ]


CANDIDATE_EPOCH_LENGTHS = [1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0]
CANDIDATE_OVERLAPS = [0.0, 0.25, 0.5]
CANDIDATES = build_candidate_grid(
    CANDIDATE_EPOCH_LENGTHS,
    CANDIDATE_OVERLAPS,
    include_baseline=True,
)


@dataclass
class WindowMetadata:
    """Metadata describing the extracted windows."""

    n_windows: int
    window_samples: int
    step_samples: int
    start_indices: np.ndarray
    sampling_mode: str
    overlap: float
    ess_proxy: float
    ess_correlation: Optional[float] = None


def create_windows_from_data(
    data: np.ndarray,
    sfreq: float,
    epoch_length_sec: float,
    overlap: float = 0.0,
    apply_hann: bool = False,
    max_windows: Optional[int] = None,
    sampling_mode: Literal["linspace", "random", "random_min_distance"] = "linspace",
    min_distance: int = 1,
    random_seed: Optional[int] = None,
    return_metadata: bool = False,
) -> Tuple[List[np.ndarray], Optional[WindowMetadata]]:
    """Create windows from continuous ROI time series.

    Notes
    -----
    For causal estimation methods such as Granger causality or LiNGAM, a Hann
    taper is usually avoided because it changes the original temporal dynamics.
    When overlap is greater than zero, the resulting windows are not independent,
    so thinning or ESS adjustment is often appropriate.

    Parameters
    ----------
    data
        Array of shape ``(n_channels, n_samples)``.
    sfreq
        Sampling frequency in Hz.
    epoch_length_sec
        Window length in seconds.
    overlap
        Fractional overlap between consecutive windows.
    apply_hann
        Whether to apply a Hann taper to each window.
    max_windows
        Optional cap on the number of returned windows.
    sampling_mode
        Strategy used when subsampling candidate window starts:
        ``"linspace"``, ``"random"``, or ``"random_min_distance"``.
    min_distance
        Minimum index distance between selected starts when using
        ``"random_min_distance"``.
    random_seed
        Optional random seed for reproducibility.
    return_metadata
        If ``True``, return a :class:`WindowMetadata` object alongside the list
        of windows.

    Returns
    -------
    windows, metadata
        A list of arrays shaped ``(n_channels, window_samples)`` and, if
        requested, associated metadata.
    """
    validate_windowing_params(epoch_length_sec, overlap, sfreq, data.shape)

    if random_seed is not None:
        np.random.seed(random_seed)

    _, n_samples = data.shape
    window_samples = int(epoch_length_sec * sfreq)
    step_samples = max(1, int(window_samples * (1 - overlap)))

    max_start = n_samples - window_samples
    if max_start < 0:
        return ([], None) if return_metadata else []

    all_starts = np.arange(0, max_start + 1, step_samples)

    if max_windows and len(all_starts) > max_windows:
        if sampling_mode == "linspace":
            selected = np.linspace(0, len(all_starts) - 1, max_windows, dtype=int)
            start_indices = all_starts[selected]
        elif sampling_mode == "random":
            selected = np.random.choice(len(all_starts), max_windows, replace=False)
            start_indices = all_starts[np.sort(selected)]
        elif sampling_mode == "random_min_distance":
            picked_starts: List[int] = []
            available = list(range(len(all_starts)))

            while len(picked_starts) < max_windows and available:
                idx = int(np.random.choice(available))
                picked_starts.append(int(all_starts[idx]))
                available = [i for i in available if abs(i - idx) > min_distance]

            start_indices = np.array(sorted(picked_starts), dtype=int)
        else:
            raise ValueError(
                "sampling_mode must be 'linspace', 'random', or 'random_min_distance'."
            )
    else:
        start_indices = all_starts

    windows: List[np.ndarray] = []
    for start in start_indices:
        window = data[:, start : start + window_samples].copy()
        if apply_hann:
            window = window * np.hanning(window_samples)
        windows.append(window)

    ess_proxy = len(windows) * (1 - overlap) if overlap > 0 else float(len(windows))

    if return_metadata:
        metadata = WindowMetadata(
            n_windows=len(windows),
            window_samples=window_samples,
            step_samples=step_samples,
            start_indices=np.asarray(start_indices),
            sampling_mode=sampling_mode,
            overlap=overlap,
            ess_proxy=float(ess_proxy),
        )
        return windows, metadata

    return windows


# ---------------------------------------------------------------------------
# Thinning and effective sample size
# ---------------------------------------------------------------------------

def thinning_indices(n_windows: int, overlap: float) -> np.ndarray:
    """Return the indices kept by a simple overlap-based thinning rule.

    The rule uses approximately ``k ~= 1 / (1 - overlap)``. For example,
    ``overlap=0.5`` yields roughly every second window.
    """
    if overlap == 0:
        return np.arange(n_windows)

    stride = max(1, int(np.round(1.0 / (1.0 - overlap))))
    return np.arange(0, n_windows, stride)


def thin_windows(
    windows: List[np.ndarray],
    overlap: float,
) -> Tuple[List[np.ndarray], np.ndarray]:
    """Thin overlapped windows to reduce short-range dependence."""
    keep = thinning_indices(len(windows), overlap)
    thinned = [windows[i] for i in keep]
    return thinned, keep


def estimate_ess(
    n_windows: int,
    overlap: float,
    method: Literal["proxy", "adjacent_corr"] = "proxy",
    windows: Optional[List[np.ndarray]] = None,
    feature_func: Optional[Callable[[np.ndarray], float]] = None,
) -> float:
    """Estimate an effective sample size (ESS) for overlapped windows.

    Parameters
    ----------
    n_windows
        Number of windows before thinning.
    overlap
        Fractional overlap.
    method
        ``"proxy"`` uses the heuristic ``ESS ~= n_windows * (1 - overlap)``.
        ``"adjacent_corr"`` estimates lag-1 dependence between neighboring
        windows using a scalar feature.
    windows
        Required when ``method="adjacent_corr"``.
    feature_func
        Function that maps a window to a scalar summary. If omitted, the mean of
        the window is used.

    Returns
    -------
    float
        Estimated effective sample size.
    """
    if n_windows <= 1:
        return float(n_windows)

    if method == "proxy":
        return max(1.0, n_windows * (1 - overlap))

    if method != "adjacent_corr":
        raise ValueError("method must be either 'proxy' or 'adjacent_corr'.")

    if windows is None or len(windows) < 2:
        return max(1.0, n_windows * (1 - overlap))

    if feature_func is None:
        feature_func = lambda w: float(np.mean(w))

    series = np.array([feature_func(w) for w in windows], dtype=float)
    if np.std(series) == 0:
        return float(n_windows)

    rho = np.corrcoef(series[:-1], series[1:])[0, 1]
    if np.isnan(rho):
        return max(1.0, n_windows * (1 - overlap))

    ess = n_windows * (1 - rho) / (1 + rho) if abs(rho) < 1 else 1.0
    return float(max(1.0, min(n_windows, ess)))


# ---------------------------------------------------------------------------
# Quality metrics
# ---------------------------------------------------------------------------

def compute_stationarity_score(windows: List[np.ndarray], alpha: float = 0.05) -> float:
    """Compute the fraction of windows that pass an ADF-based stationarity check.

    A window is counted as stationary if at least half of its ROI time series
    reject the unit-root null hypothesis at the chosen alpha level.
    """
    if not windows:
        return 0.0

    passes = 0
    for window in windows:
        roi_passes = 0
        n_rois = window.shape[0]

        for roi_idx in range(n_rois):
            signal = window[roi_idx]
            if np.std(signal) == 0:
                continue
            try:
                p_value = adfuller(signal, autolag="AIC")[1]
                if p_value < alpha:
                    roi_passes += 1
            except Exception:
                continue

        if roi_passes >= max(1, n_rois // 2):
            passes += 1

    return passes / len(windows)


def compute_fit_quality_score(windows: List[np.ndarray], lag: int = 2) -> float:
    """Estimate VAR fit quality as the fraction of windows that fit successfully.

    This metric is deliberately simple: if a VAR model of the requested lag
    fits without error and produces finite residuals, the window counts as a
    successful fit.
    """
    if not windows:
        return 0.0

    successes = 0
    for window in windows:
        try:
            model = VAR(window.T)
            result = model.fit(lag)
            resid = result.resid
            if np.all(np.isfinite(resid)):
                successes += 1
        except Exception:
            continue

    return successes / len(windows)


def compute_simple_connectivity(
    windows: List[np.ndarray],
    threshold: float = 0.3,
) -> np.ndarray:
    """Build a simple ROI-by-ROI connectivity summary from window correlations.

    The function is intentionally lightweight and is used only for stability
    scoring. It should not be confused with the final Granger or LiNGAM
    connectivity estimates.
    """
    if not windows:
        return np.empty((0, 0))

    n_rois = windows[0].shape[0]
    stacked = np.concatenate([w.T for w in windows], axis=0)
    corr = np.corrcoef(stacked, rowvar=False)
    corr = np.nan_to_num(np.abs(corr), nan=0.0)
    np.fill_diagonal(corr, 0.0)
    corr[corr < threshold] = 0.0
    return corr


def compute_stability_score(
    windows: List[np.ndarray],
    n_splits: int = 5,
    random_seed: int = 42,
    threshold: float = 0.3,
) -> float:
    """Estimate split-half stability of a simple connectivity surrogate.

    The windows are repeatedly shuffled, split into two halves, converted into
    lightweight connectivity matrices, and then compared by Pearson
    correlation over the flattened upper-level entries.
    """
    if len(windows) < 4:
        return 0.0

    rng = np.random.default_rng(random_seed)
    scores: List[float] = []

    for _ in range(n_splits):
        indices = np.arange(len(windows))
        rng.shuffle(indices)
        mid = len(indices) // 2
        first = [windows[i] for i in indices[:mid]]
        second = [windows[i] for i in indices[mid:]]

        if not first or not second:
            continue

        conn_a = compute_simple_connectivity(first, threshold=threshold)
        conn_b = compute_simple_connectivity(second, threshold=threshold)

        if conn_a.size == 0 or conn_b.size == 0:
            continue

        flat_a = conn_a.ravel()
        flat_b = conn_b.ravel()
        if np.std(flat_a) == 0 or np.std(flat_b) == 0:
            continue

        corr = np.corrcoef(flat_a, flat_b)[0, 1]
        if np.isfinite(corr):
            scores.append(float(corr))

    return float(np.mean(scores)) if scores else 0.0


# ---------------------------------------------------------------------------
# Candidate evaluation and sweep
# ---------------------------------------------------------------------------

def evaluate_candidate(
    data: np.ndarray,
    sfreq: float,
    epoch_length_sec: float,
    overlap: float,
    max_windows: int = 30,
    apply_thinning: bool = True,
    ess_method: str = "adjacent_corr",
    sampling_mode: str = "linspace",
    random_seed: Optional[int] = None,
    verbose: bool = False,
) -> Dict[str, float]:
    """Evaluate one `(epoch_length_sec, overlap)` candidate.

    Returns a compact metrics dictionary that can be appended to a sweep table.
    """
    windows, metadata = create_windows_from_data(
        data,
        sfreq,
        epoch_length_sec,
        overlap=overlap,
        max_windows=max_windows,
        sampling_mode=sampling_mode,
        random_seed=random_seed,
        return_metadata=True,
    )

    if metadata is None or len(windows) == 0:
        return {
            "n_windows_raw": 0,
            "n_windows_thinned": 0,
            "ess_proxy": 0.0,
            "ess_estimated": 0.0,
            "stationarity_score": 0.0,
            "fit_quality_score": 0.0,
            "stability_score": 0.0,
            "thinning_applied": False,
        }

    windows_for_analysis = windows
    n_thinned = len(windows)

    if apply_thinning and overlap > 0:
        windows_for_analysis, kept = thin_windows(windows, overlap)
        n_thinned = len(kept)

    if ess_method == "adjacent_corr" and len(windows_for_analysis) > 1:
        ess = estimate_ess(
            len(windows_for_analysis),
            overlap,
            method="adjacent_corr",
            windows=windows_for_analysis,
        )
    else:
        ess = float(metadata.ess_proxy if not apply_thinning else n_thinned)

    stationarity = compute_stationarity_score(windows_for_analysis)
    fit_quality = compute_fit_quality_score(windows_for_analysis, lag=2)
    stability = compute_stability_score(windows_for_analysis, n_splits=5)

    if verbose:
        print(f"Evaluated candidate: epoch={epoch_length_sec}s, overlap={overlap}")
        print(f"  Raw windows: {len(windows)}")
        print(f"  Windows used for scoring: {n_thinned}")
        print(f"  Estimated ESS: {ess:.1f}")
        print(f"  Stationarity score: {stationarity:.3f}")
        print(f"  Fit quality score: {fit_quality:.3f}")
        print(f"  Stability score: {stability:.3f}")

    return {
        "n_windows_raw": len(windows),
        "n_windows_thinned": n_thinned,
        "ess_proxy": float(metadata.ess_proxy),
        "ess_estimated": float(ess),
        "stationarity_score": float(stationarity),
        "fit_quality_score": float(fit_quality),
        "stability_score": float(stability),
        "thinning_applied": bool(apply_thinning and overlap > 0),
    }


def run_stability_sweep(
    data: np.ndarray,
    sfreq: float,
    candidates: List[Dict],
    max_windows: int = 30,
    sampling_mode: str = "linspace",
    apply_thinning: bool = True,
    ess_method: str = "adjacent_corr",
    random_seed: Optional[int] = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """Evaluate a grid of windowing candidates and return a summary table."""
    results = []

    iterator = tqdm(candidates, desc="Evaluating candidates") if verbose else candidates
    for cand in iterator:
        metrics = evaluate_candidate(
            data=data,
            sfreq=sfreq,
            epoch_length_sec=cand["epoch_length_sec"],
            overlap=cand["overlap"],
            max_windows=max_windows,
            apply_thinning=apply_thinning,
            ess_method=ess_method,
            sampling_mode=sampling_mode,
            random_seed=random_seed,
            verbose=False,
        )
        results.append(
            {
                "epoch_length_sec": cand["epoch_length_sec"],
                "overlap": cand["overlap"],
                **metrics,
            }
        )

    df = pd.DataFrame(results)

    for metric in ["stationarity_score", "fit_quality_score", "stability_score"]:
        min_val = df[metric].min()
        max_val = df[metric].max()
        if max_val > min_val:
            df[f"{metric}_norm"] = (df[metric] - min_val) / (max_val - min_val)
        else:
            df[f"{metric}_norm"] = 0.5

    return df


# ---------------------------------------------------------------------------
# Selection strategies
# ---------------------------------------------------------------------------

def select_by_constraint_first(
    df: pd.DataFrame,
    stationarity_min: float = 0.70,
    fit_quality_min: float = 0.60,
) -> Tuple[Dict, str]:
    """Select the best candidate after applying minimum-quality constraints."""
    filtered = df[
        (df["stationarity_score"] >= stationarity_min)
        & (df["fit_quality_score"] >= fit_quality_min)
    ].copy()

    if len(filtered) == 0:
        justification = (
            "No candidate satisfied the minimum stationarity and fit-quality "
            "constraints, so the full table was considered."
        )
        filtered = df.copy()
    else:
        justification = (
            "Candidates were first filtered by minimum stationarity and fit-quality "
            "constraints before ranking."
        )

    filtered = filtered.sort_values(
        by=["stability_score", "stationarity_score", "overlap", "epoch_length_sec"],
        ascending=[False, False, True, True],
    )

    best = filtered.iloc[0].to_dict()
    justification += (
        f"\nSelected candidate: epoch={best['epoch_length_sec']}s, "
        f"overlap={best['overlap']}"
        f"\n  Stability: {best['stability_score']:.3f}"
        f"\n  Stationarity: {best['stationarity_score']:.3f}"
        f"\n  Fit quality: {best['fit_quality_score']:.3f}"
    )
    return best, justification


def select_by_pareto_knee(df: pd.DataFrame) -> Tuple[Dict, str]:
    """Select a candidate from the Pareto front using distance to the ideal point."""
    metrics = [
        "stationarity_score_norm",
        "fit_quality_score_norm",
        "stability_score_norm",
    ]

    pareto_indices = []
    for i, row_i in df.iterrows():
        is_pareto = True
        for j, row_j in df.iterrows():
            if i == j:
                continue
            if all(row_j[m] >= row_i[m] for m in metrics) and any(
                row_j[m] > row_i[m] for m in metrics
            ):
                is_pareto = False
                break
        if is_pareto:
            pareto_indices.append(i)

    pareto_df = df.loc[pareto_indices]
    ideal = np.array([1.0, 1.0, 1.0])

    distances = []
    for _, row in pareto_df.iterrows():
        point = np.array([row[m] for m in metrics])
        distances.append(np.linalg.norm(ideal - point))

    knee_idx = pareto_df.index[int(np.argmin(distances))]
    best = df.loc[knee_idx].to_dict()

    justification = (
        f"Pareto-front selection retained {len(pareto_df)} of {len(df)} candidates. "
        "The final choice is the Pareto point closest to the ideal normalized score "
        "vector (1, 1, 1)."
        f"\n  Distance to ideal: {min(distances):.3f}"
    )
    return best, justification


def select_by_rank_aggregation(df: pd.DataFrame) -> Tuple[Dict, str]:
    """Select a candidate by Borda-style rank aggregation across core metrics."""
    metrics = ["stationarity_score", "fit_quality_score", "stability_score"]
    n_candidates = len(df)
    borda_scores = np.zeros(n_candidates)

    for metric in metrics:
        ranks = df[metric].rank(ascending=False, method="min").values - 1
        borda_scores += n_candidates - ranks

    df = df.copy()
    df["borda_score"] = borda_scores
    best_idx = df["borda_score"].idxmax()
    best = df.loc[best_idx].to_dict()

    justification = (
        "Rank aggregation was computed with a Borda-style score over stationarity, "
        "fit quality, and stability."
        f"\n  Borda score: {best['borda_score']:.1f}/{n_candidates * 3}"
    )
    return best, justification


def select_by_entropy_weighting(df: pd.DataFrame) -> Tuple[Dict, str]:
    """Select a candidate using entropy-derived weights for normalized metrics."""
    metrics = [
        "stationarity_score_norm",
        "fit_quality_score_norm",
        "stability_score_norm",
    ]

    entropies = []
    for metric in metrics:
        values = np.clip(df[metric].values, 1e-10, 1.0)
        probs = values / values.sum()
        entropy = -np.sum(probs * np.log(probs))
        entropies.append(entropy)

    entropies = np.array(entropies, dtype=float)
    max_entropy = np.log(len(df)) if len(df) > 1 else 1.0
    normalized = entropies / max_entropy
    weights = 1 - normalized
    weights = weights / weights.sum()

    df = df.copy()
    df["weighted_score"] = sum(weights[i] * df[m] for i, m in enumerate(metrics))
    best_idx = df["weighted_score"].idxmax()
    best = df.loc[best_idx].to_dict()

    justification = (
        "Entropy weighting assigned larger weights to the normalized metrics with "
        "greater discriminatory power across candidates."
        f"\n  Weights: stationarity={weights[0]:.3f}, "
        f"fit_quality={weights[1]:.3f}, stability={weights[2]:.3f}"
        f"\n  Weighted score: {best['weighted_score']:.3f}"
    )
    return best, justification
