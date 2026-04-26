"""Tests for dedup checks."""

import pytest
from auditor.checks import dedup


def test_find_exact_duplicates(df_dirty):
    """Test exact duplicate detection."""
    issues = dedup.find_exact_duplicates(df_dirty)
    assert any(i["check"] == "exact_duplicates" for i in issues)


def test_find_near_duplicates_small():
    """Test small dataset near-dup detection."""
    import pandas as pd
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    issues = dedup.find_near_duplicates_small(df, 0.95)
    assert isinstance(issues, list)