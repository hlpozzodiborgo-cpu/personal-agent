"""
Unit tests for Stage 2 signal detection helpers.

No model loading, no DB, no network — pure unit tests.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from agent.stage2_signals import (
    build_signal_summary,
    classify_strength,
    compute_authority,
    compute_velocity,
)


# ---------------------------------------------------------------------------
# compute_authority
# ---------------------------------------------------------------------------

class TestComputeAuthority:
    def test_two_tier1_one_tier5(self):
        """tier1=1.0, tier5=0.2 → mean (1.0+1.0+0.2)/3 ≈ 0.733."""
        arts = [
            MagicMock(source_tier=1),
            MagicMock(source_tier=1),
            MagicMock(source_tier=5),
        ]
        result = compute_authority(arts)
        assert 0.7 < result < 0.8

    def test_all_tier3(self):
        """All tier-3 sources → authority exactly 0.6."""
        arts = [MagicMock(source_tier=3) for _ in range(5)]
        assert compute_authority(arts) == pytest.approx(0.6, abs=0.01)

    def test_single_tier1(self):
        assert compute_authority([MagicMock(source_tier=1)]) == pytest.approx(1.0)

    def test_single_tier5(self):
        assert compute_authority([MagicMock(source_tier=5)]) == pytest.approx(0.2)


# ---------------------------------------------------------------------------
# compute_velocity
# ---------------------------------------------------------------------------

class TestComputeVelocity:
    def test_zero_when_single_article(self):
        arts = [MagicMock(published_at=datetime(2026, 5, 12, 10, 0, 0))]
        assert compute_velocity(arts) == 0.0

    def test_zero_when_same_hour(self):
        """All articles within the same hour → velocity = 0.0."""
        ts = datetime(2026, 5, 12, 10, 0, 0)
        arts = [MagicMock(published_at=ts) for _ in range(3)]
        assert compute_velocity(arts) == 0.0

    def test_normal_case(self):
        """4 articles spread over 2 hours → velocity ≈ 2.0."""
        base = datetime(2026, 5, 12, 10, 0, 0)
        arts = [
            MagicMock(published_at=base),
            MagicMock(published_at=base + timedelta(hours=2)),
            MagicMock(published_at=base + timedelta(hours=1)),
            MagicMock(published_at=base + timedelta(hours=1, minutes=30)),
        ]
        v = compute_velocity(arts)
        assert 1.5 < v < 2.5

    def test_clamped_at_20(self):
        """Pathological case: many articles in a 1h window → clamped to 20."""
        base = datetime(2026, 5, 12, 10, 0, 0)
        arts = [
            MagicMock(published_at=base + timedelta(minutes=i))
            for i in range(50)
        ]
        # span = 49 min < 1h → velocity = 0.0 (span < 1h)
        # Let me use span > 1h
        arts[-1] = MagicMock(published_at=base + timedelta(hours=2))
        assert compute_velocity(arts) == pytest.approx(20.0)

    def test_zero_when_no_published_at(self):
        arts = [MagicMock(published_at=None) for _ in range(3)]
        assert compute_velocity(arts) == 0.0


# ---------------------------------------------------------------------------
# classify_strength
# ---------------------------------------------------------------------------

class TestClassifyStrength:
    def test_strong_tier1_and_novelty(self):
        """volume=3, tier1 source, novelty=1.0 → strong."""
        assert classify_strength(
            volume=3, authority=0.7, velocity=1.0,
            novelty=1.0, has_tier1_source=True,
        ) == "strong"

    def test_strong_high_volume_high_authority(self):
        """volume=4, authority=0.5 (>=0.45) → strong."""
        assert classify_strength(
            volume=4, authority=0.5, velocity=0.5,
            novelty=0.5, has_tier1_source=False,
        ) == "strong"

    def test_strong_high_volume(self):
        """volume=5, authority=0.5, velocity=1.0 → strong (first condition)."""
        assert classify_strength(
            volume=5, authority=0.5, velocity=1.0,
            novelty=0.5, has_tier1_source=False,
        ) == "strong"

    def test_medium_basic(self):
        """volume=3, low authority → medium (third condition: volume>=3)."""
        assert classify_strength(
            volume=3, authority=0.3, velocity=0.5,
            novelty=0.5, has_tier1_source=False,
        ) == "medium"

    def test_medium_authority(self):
        """volume=2, authority=0.6 → medium (volume>=2 AND authority>=0.4)."""
        assert classify_strength(
            volume=2, authority=0.6, velocity=0.5,
            novelty=0.5, has_tier1_source=False,
        ) == "medium"

    def test_weak_below_threshold(self):
        """volume=1 → weak."""
        assert classify_strength(
            volume=1, authority=0.3, velocity=0.5,
            novelty=0.5, has_tier1_source=False,
        ) == "weak"

    def test_weak_low_authority(self):
        """volume=2, authority=0.3 (< 0.4) → weak."""
        assert classify_strength(
            volume=2, authority=0.3, velocity=0.5,
            novelty=0.5, has_tier1_source=False,
        ) == "weak"

    def test_not_strong_without_tier1_even_with_novelty(self):
        """volume=3, novelty=1.0 but NO tier1 source → NOT strong via that condition."""
        result = classify_strength(
            volume=3, authority=0.3, velocity=0.5,
            novelty=1.0, has_tier1_source=False,
        )
        # Falls to medium via volume >= 3
        assert result == "medium"


# ---------------------------------------------------------------------------
# build_signal_summary
# ---------------------------------------------------------------------------

class TestBuildSummary:
    def test_includes_longest_title(self):
        arts = [
            MagicMock(title="Apple beats earnings expectations massively",
                      source="reuters.com", source_tier=1),
            MagicMock(title="AAPL up", source="bloomberg.com", source_tier=1),
        ]
        summary = build_signal_summary(arts)
        assert "Apple beats earnings expectations massively" in summary

    def test_includes_sources(self):
        arts = [
            MagicMock(title="Apple beats earnings expectations massively",
                      source="reuters.com", source_tier=1),
            MagicMock(title="AAPL up", source="bloomberg.com", source_tier=1),
        ]
        summary = build_signal_summary(arts)
        assert "reuters.com" in summary
        assert "bloomberg.com" in summary

    def test_truncated_at_500_chars(self):
        long_title = "A" * 600
        arts = [MagicMock(title=long_title, source="x.com", source_tier=3)]
        assert len(build_signal_summary(arts)) <= 500

    def test_at_most_3_sources(self):
        arts = [
            MagicMock(title=f"title {i}", source=f"source{i}.com", source_tier=3)
            for i in range(6)
        ]
        summary = build_signal_summary(arts)
        # At most 3 sources appear after "sources: "
        sources_part = summary.split("— sources: ")[-1]
        assert sources_part.count(".com") <= 3
