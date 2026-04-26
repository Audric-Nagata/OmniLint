"""Tests for distribution checks."""

import pytest
from auditor.checks import distribution


def test_check_skewness():
    """Test skewness detection."""
    import pandas as pd
    import numpy as np
    df = pd.DataFrame({"val": np.random.lognormal(0, 1, 1000)})
    issues = distribution.check_skewness(df)
    assert any(i["check"] == "skewness" for i in issues)


def test_check_outliers_iqr():
    """Test IQR outlier detection."""
    import pandas as pd
    df = pd.DataFrame({"val": [1, 2, 3, 4, 5, 100]})
    issues = distribution.check_outliers_iqr(df)
    assert any(i["check"] == "outliers_iqr" for i in issues)


def test_check_outliers_zscore():
    """Test Z-score outlier detection."""
    import pandas as pd
    df = pd.DataFrame({"val": [1, 2, 3, 4, 5, 100]})
    issues = distribution.check_outliers_zscore(df)
    assert any(i["check"] == "outliers_zscore" for i in issues)