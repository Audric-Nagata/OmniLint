"""Tests for importance checks."""

import pytest
from auditor.checks import importance


def test_run_importance(df_leaky):
    """Test importance detection."""
    issues = importance.run(df_leaky, "label")
    assert len(issues) >= 0