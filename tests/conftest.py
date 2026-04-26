"""Pytest fixtures for tests."""

import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def df_clean():
    """Clean dataset with no issues."""
    np.random.seed(42)
    n = 1000
    return pd.DataFrame({
        "age": np.random.randint(18, 70, n),
        "income": np.random.normal(50000, 15000, n),
        "score": np.random.uniform(0, 1, n),
        "label": np.random.choice(["a", "b"], n),
    })


@pytest.fixture
def df_dirty():
    """Dataset with common quality issues."""
    np.random.seed(42)
    n = 1000
    df = pd.DataFrame({
        "age": np.random.randint(18, 70, n),
        "income": np.random.normal(50000, 15000, n),
        "score": np.random.uniform(0, 1, n),
        "label": np.random.choice(["a", "b"], n),
    })
    df.loc[:50, "income"] = np.nan
    df.loc[100:110] = df.loc[0:10]
    df["constant"] = "US"
    return df


@pytest.fixture
def df_imbalanced():
    """Dataset with class imbalance."""
    np.random.seed(42)
    n = 1000
    labels = ["legit"] * 980 + ["fraud"] * 20
    return pd.DataFrame({
        "age": np.random.randint(18, 70, n),
        "income": np.random.normal(50000, 15000, n),
        "label": labels,
    })


@pytest.fixture
def df_leaky():
    """Dataset with leaky feature."""
    np.random.seed(42)
    n = 1000
    return pd.DataFrame({
        "age": np.random.randint(18, 70, n),
        "income": np.random.normal(50000, 15000, n),
        "approval_score": np.random.choice([0, 1], n, p=[0.03, 0.97]),
        "label": np.random.choice(["a", "b"], n),
    })


@pytest.fixture
def df_large():
    """Large dataset for FAISS testing."""
    np.random.seed(42)
    n = 15000
    return pd.DataFrame({
        "f1": np.random.randn(n),
        "f2": np.random.randn(n),
        "f3": np.random.randn(n),
        "f4": np.random.randn(n),
        "f5": np.random.randn(n),
    })