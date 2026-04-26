"""Tests for basic checks."""

import pytest
from auditor.checks import basic


def test_check_missing(df_dirty):
    """Test missing value detection."""
    issues = basic.check_missing(df_dirty, threshold=0.05)
    assert any(i["check"] == "missing_values" for i in issues)


def test_check_constants(df_dirty):
    """Test constant column detection."""
    issues = basic.check_constants(df_dirty)
    assert any(i["check"] == "constant_column" for i in issues)


def test_check_exact_duplicates(df_dirty):
    """Test duplicate detection."""
    issues = basic.check_exact_duplicates(df_dirty)
    assert any(i["check"] == "exact_duplicates" for i in issues)


def test_clean_data_no_issues(df_clean):
    """Test clean data produces no issues."""
    issues = basic.run(df_clean)
    assert len(issues) == 0