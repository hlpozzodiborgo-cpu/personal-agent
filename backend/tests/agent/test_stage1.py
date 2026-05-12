"""
Unit tests for Stage 1 ingestion helpers.

All tests are fully offline — no real HTTP calls are made.
"""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agent.sources.gdelt import fetch_recent_articles
from agent.stage1_ingest import (
    classify_event,
    dedupe_articles,
    extract_tickers,
    score_sentiment,
)


# ---------------------------------------------------------------------------
# GDELT fetch tests
# ---------------------------------------------------------------------------

class TestFetchRecentArticles:
    def test_returns_empty_on_http_error(self):
        """Non-200 response must yield an empty list without raising."""
        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("agent.sources.gdelt.httpx.AsyncClient", return_value=mock_client):
            result = asyncio.run(fetch_recent_articles(["AAPL"], hours_back=6))

        assert result == []

    def test_parses_valid_gdelt_response(self):
        """200 response with articles list must be parsed into normalized dicts."""
        fake_payload = {
            "articles": [
                {
                    "url":      "https://reuters.com/article/apple-earnings",
                    "title":    "Apple beats earnings expectations",
                    "seendate": "20240315T143022Z",
                    "domain":   "reuters.com",
                    "language": "English",
                }
            ]
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value=fake_payload)

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("agent.sources.gdelt.httpx.AsyncClient", return_value=mock_client):
            result = asyncio.run(fetch_recent_articles(["AAPL"], hours_back=6))

        assert len(result) == 1
        art = result[0]
        assert art["url"]    == "https://reuters.com/article/apple-earnings"
        assert art["title"]  == "Apple beats earnings expectations"
        assert art["source"] == "reuters.com"
        assert "2024-03-15" in art["published_at"]

    def test_filters_non_latin_titles(self):
        """Articles with CJK/Arabic/Korean titles must be dropped."""
        fake_payload = {
            "articles": [
                {
                    "url": "https://reuters.com/ok",
                    "title": "Apple earnings beat",
                    "seendate": "20240315T143022Z",
                    "domain": "reuters.com",
                    "language": "English",
                },
                {
                    "url": "https://sina.com/cn",
                    "title": "华为 Pura X Max 卖爆了",
                    "seendate": "20240315T143022Z",
                    "domain": "sina.com",
                    "language": "Chinese",
                },
            ]
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value=fake_payload)

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("agent.sources.gdelt.httpx.AsyncClient", return_value=mock_client):
            result = asyncio.run(fetch_recent_articles(["AAPL"], hours_back=6))

        assert len(result) == 1
        assert result[0]["title"] == "Apple earnings beat"


# ---------------------------------------------------------------------------
# Deduplication tests
# ---------------------------------------------------------------------------

class TestDedupeArticles:
    def test_removes_duplicate_url_after_canonicalization(self):
        """Two articles sharing the same canonical URL must be collapsed to one."""
        articles = [
            {"url": "https://www.reuters.com/article/foo?utm_source=twitter", "title": "Foo story one"},
            {"url": "https://reuters.com/article/foo", "title": "Foo story duplicate"},
        ]
        result = dedupe_articles(articles)
        assert len(result) == 1
        assert result[0]["title"] == "Foo story one"

    def test_keeps_genuinely_distinct_articles(self):
        """Different URLs with different titles must both be kept."""
        articles = [
            {"url": "https://reuters.com/article/apple",    "title": "Apple earnings beat"},
            {"url": "https://bloomberg.com/news/msft-deal", "title": "Microsoft announces Azure deal"},
        ]
        result = dedupe_articles(articles)
        assert len(result) == 2


# ---------------------------------------------------------------------------
# Sentiment tests
# ---------------------------------------------------------------------------

class TestScoreSentiment:
    def test_score_is_within_valid_range(self):
        """Non-zero score must stay in [-1.0, 1.0]; None is also valid."""
        score = score_sentiment("great profit record earnings", "investors celebrate")
        assert score is None or -1.0 <= score <= 1.0

    def test_positive_headline_scores_positive(self):
        """Clearly positive headline should yield a score > 0."""
        score = score_sentiment("outstanding growth record profits beat expectations", "")
        assert score is not None and score > 0.0

    def test_negative_headline_scores_negative(self):
        """Clearly negative headline should yield a score < 0."""
        score = score_sentiment("terrible crash collapse bankruptcy fraud scandal", "")
        assert score is not None and score < 0.0

    def test_neutral_text_returns_none(self):
        """Text with no VADER lexicon words must return None, not 0.0."""
        assert score_sentiment("the the the", "") is None


# ---------------------------------------------------------------------------
# Ticker extraction tests
# ---------------------------------------------------------------------------

class TestExtractTickers:
    def test_dollar_notation(self):
        known = ["AAPL", "MSFT"]
        assert extract_tickers("$AAPL is up", known) == ["AAPL"]

    def test_company_name_alias(self):
        known = ["AAPL", "MC.PA"]
        result = extract_tickers("LVMH and Apple beat expectations", known)
        assert set(result) == {"AAPL", "MC.PA"}

    def test_bigram_alias(self):
        known = ["MC.PA"]
        result = extract_tickers("Louis Vuitton expands in Asia", known)
        assert "MC.PA" in result

    def test_handles_plural(self):
        """iPhones (plural) must resolve to AAPL via rstrip('s') fallback."""
        known = ["AAPL"]
        assert "AAPL" in extract_tickers("Supported iPhones launch soon", known)

    def test_finds_vision_pro(self):
        """'Vision Pro' bigram alias must resolve to AAPL."""
        known = ["AAPL"]
        assert "AAPL" in extract_tickers("Vision Pro update arrives", known)


# ---------------------------------------------------------------------------
# Event classification tests
# ---------------------------------------------------------------------------

class TestClassifyEvent:
    def test_earnings(self):
        assert classify_event("Q3 earnings beat estimates", "") == "earnings"

    def test_merger_acquisition(self):
        assert classify_event("Airbus acquires startup", "") == "merger_acquisition"

    def test_regulatory_settlement(self):
        assert classify_event("Apple settles iPhone lawsuit for $250M", "") == "regulatory"

    def test_other_fallback(self):
        assert classify_event("Random news headline", "") == "other"

    def test_sport_not_classified_as_macro(self):
        """'Pirates' must not trigger the macro keyword 'rate'."""
        assert classify_event("Rockies vs Pirates Series May 12", "") == "other"


# ---------------------------------------------------------------------------
# YFinance source tests
# ---------------------------------------------------------------------------

import time as _time

from agent.sources.yfinance import YFinanceSource


class TestYFinanceSource:
    def test_returns_articles_within_time_window(self):
        """Articles older than hours_back must be filtered out."""
        now = int(_time.time())
        mock_news = [
            {
                "title": "Apple beats Q3 earnings",
                "link":  "https://reuters.com/article/apple-earnings",
                "providerPublishTime": now - 3600,    # 1h ago — inside 24h window
            },
            {
                "title": "Old Apple story from two days ago",
                "link":  "https://reuters.com/article/apple-old",
                "providerPublishTime": now - 48 * 3600,  # 48h ago — outside window
            },
        ]
        with patch("agent.sources.yfinance.yf.Ticker") as MockTicker:
            MockTicker.return_value.news = mock_news
            result = asyncio.run(YFinanceSource().fetch(["AAPL"], hours_back=24))

        assert len(result) == 1
        assert result[0]["title"] == "Apple beats Q3 earnings"

    def test_handles_ticker_failure_gracefully(self):
        """A failing ticker must not block the others."""
        now = int(_time.time())

        def _ticker_factory(sym: str):
            if sym == "BAD":
                raise Exception("unknown ticker BAD")
            m = MagicMock()
            m.news = [{
                "title": "AAPL news headline",
                "link":  "https://cnbc.com/aapl-news",
                "providerPublishTime": now - 3600,
            }]
            return m

        with patch("agent.sources.yfinance.yf.Ticker", side_effect=_ticker_factory):
            result = asyncio.run(YFinanceSource().fetch(["BAD", "AAPL"], hours_back=24))

        assert len(result) == 1
        assert result[0]["title"] == "AAPL news headline"

    def test_extracts_domain_from_link(self):
        """The source field must be the bare domain without www. prefix."""
        now = int(_time.time())
        mock_news = [{
            "title": "Apple supply chain update",
            "link":  "https://www.reuters.com/article/apple-supply-chain",
            "providerPublishTime": now - 3600,
        }]
        with patch("agent.sources.yfinance.yf.Ticker") as MockTicker:
            MockTicker.return_value.news = mock_news
            result = asyncio.run(YFinanceSource().fetch(["AAPL"], hours_back=24))

        assert result[0]["source"] == "reuters.com"
