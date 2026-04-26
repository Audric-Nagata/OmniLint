"""Tests for scorer."""

import pytest
from auditor.core import scorer


def test_compute():
    """Test DQS computation."""
    findings = {
        "missing_values": [{"severity": "high"}],
        "duplicates": [{"severity": "medium"}],
    }
    result = scorer.compute(findings)
    assert 0 <= result.quality_score <= 100
    assert result.score_band in ["Critical", "Poor", "Fair", "Good"]


def test_get_band():
    """Test score band mapping."""
    assert scorer.get_band(90) == "Good"
    assert scorer.get_band(75) == "Fair"
    assert scorer.get_band(50) == "Poor"
    assert scorer.get_band(20) == "Critical"