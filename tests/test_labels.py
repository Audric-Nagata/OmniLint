"""Tests for label checks."""

import pytest
from auditor.checks import labels


def test_check_imbalance(df_imbalanced):
    """Test class imbalance detection."""
    issues = labels.check_imbalance(df_imbalanced, "label")
    assert any(i["check"] == "class_imbalance" for i in issues)


def test_check_rare_classes(df_imbalanced):
    """Test rare class detection."""
    issues = labels.check_rare_classes(df_imbalanced, "label", min_samples=50)
    assert any(i["check"] == "rare_class" for i in issues)


def test_no_target_no_issues():
    """Test no issues when no target column."""
    import pandas as pd
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    issues = labels.run(df, "nonexistent")
    assert len(issues) == 0