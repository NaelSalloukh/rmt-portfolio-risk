"""Random matrix theory tools for separating signal from noise in correlation matrices."""

import numpy as np


def mp_bounds(q, s2=1.0):
    """Lower and upper edges of the Marchenko-Pastur noise band for q = N/T and noise variance s2."""
    return s2 * (1 - np.sqrt(q)) ** 2, s2 * (1 + np.sqrt(q)) ** 2


def mp_density(x, q, s2=1.0):
    """Marchenko-Pastur density: the eigenvalue distribution of a pure-noise correlation matrix."""
    lo, hi = mp_bounds(q, s2)
    x = np.asarray(x, float)
    return np.sqrt(np.clip((hi - x) * (x - lo), 0, None)) / (2 * np.pi * q * s2 * x)


def eig(C):
    """Eigenvalues and eigenvectors of a symmetric matrix, largest eigenvalue first."""
    w, v = np.linalg.eigh(C)
    return w[::-1], v[:, ::-1]


def n_signal(w, q, s2=1.0):
    """Number of eigenvalues above the upper Marchenko-Pastur edge."""
    return int((w > mp_bounds(q, s2)[1]).sum())


def ipr(v):
    """Inverse participation ratio of each eigenvector: about 1/N if spread evenly, 1 if on a single stock."""
    return (v ** 4).sum(axis=0)


def clean_corr(C, q, k=None):
    """Eigenvalue clipping: keep the k largest eigenvalues, replace the rest with their average, rescale to unit diagonal."""
    w, v = eig(C)
    k = n_signal(w, q) if k is None else k
    w = w.copy()
    w[k:] = w[k:].mean()
    Cc = (v * w) @ v.T
    d = np.sqrt(np.diag(Cc))
    return Cc / np.outer(d, d)


def clean_cov(X, k=None):
    """Cleaned covariance matrix from a T x N array of returns: clean the correlations, keep each stock's volatility."""
    T, N = X.shape
    S = np.cov(X, rowvar=False)
    sd = np.sqrt(np.diag(S))
    return clean_corr(S / np.outer(sd, sd), N / T, k) * np.outer(sd, sd)


def shuffle_eigs(X, n=20, seed=0):
    """Eigenvalues after shuffling each stock's returns in time, n times: keeps fat tails, destroys correlation."""
    rng = np.random.default_rng(seed)
    return np.array([eig(np.corrcoef(rng.permuted(X, axis=0), rowvar=False))[0] for _ in range(n)])


def min_var(S):
    """Global minimum-variance portfolio weights for covariance matrix S, summing to 1 (short positions allowed)."""
    w = np.linalg.solve(S, np.ones(len(S)))
    return w / w.sum()
