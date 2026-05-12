"""
Ticker aliases and source quality tiers.

TICKER_ALIASES: maps canonical symbol → list of company/product names to match in article text.
SOURCE_TIERS:   maps domain → tier int (1 = most authoritative, 5 = least).
"""
from __future__ import annotations

TICKER_ALIASES: dict[str, list[str]] = {
    "AAPL":   ["Apple", "iPhone", "iPad", "MacBook", "App Store", "Vision Pro", "visionOS", "macOS"],
    "MSFT":   ["Microsoft", "Azure", "Office", "Windows", "Copilot"],
    "GOOGL":  ["Alphabet", "Google", "DeepMind", "YouTube", "Waymo"],
    "AMZN":   ["Amazon", "AWS", "Alexa", "Prime"],
    "NVDA":   ["Nvidia", "CUDA", "GeForce", "Blackwell"],
    "META":   ["Meta", "Facebook", "Instagram", "WhatsApp", "Llama"],
    "TSLA":   ["Tesla", "Elon Musk", "Cybertruck", "Autopilot"],
    "BNP.PA": ["BNP Paribas", "BNP"],
    "ESE.PA": ["Eurazeo"],
    "MC.PA":  ["LVMH", "Louis Vuitton", "Moët", "Hennessy"],
    "AIR.PA": ["Airbus"],
    "SAN.PA": ["Sanofi"],
    "TTE.PA": ["TotalEnergies", "TotalEnergies SE", "Total"],
}

# Reverse lookup built once at import time: name (lower) → symbol
_ALIAS_TO_TICKER: dict[str, str] = {
    alias.lower(): symbol
    for symbol, aliases in TICKER_ALIASES.items()
    for alias in aliases
}


def alias_to_ticker(name: str) -> str | None:
    """Return canonical ticker for a company name, or None if unknown."""
    return _ALIAS_TO_TICKER.get(name.lower())


SOURCE_TIERS: dict[str, int] = {
    "reuters.com":       1,
    "bloomberg.com":     1,
    "ft.com":            1,
    "wsj.com":           1,
    "apnews.com":        1,
    "bbc.com":           1,
    "bbc.co.uk":         1,
    "lesechos.fr":       1,
    "lemonde.fr":        1,
    "seekingalpha.com":  2,
    "marketwatch.com":   2,
    "cnbc.com":          2,
    "forbes.com":        2,
    "businessinsider.com": 2,
    "gdelt":             3,  # generic GDELT source placeholder
    # Yahoo Finance sources
    "finance.yahoo.com": 2,
    "yahoo.com":         2,
    "youtube.com":       5,
    "fool.com":          3,
    "investorplace.com": 3,
    "barrons.com":       1,
    "thestreet.com":     3,
    "default":           3,
}
