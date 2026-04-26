"""Tests for leakage detection."""

import pytest
from auditor.checks import leakage


def test_check_numeric_leakage(df_leaky):
    """Test numeric leakage detection."""
    issues = leakage.run(df_leaky, "label")
    assert any(i["check"] == "leakage_correlation" for i in issues)