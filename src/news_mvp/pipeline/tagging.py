from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(slots=True)
class TagMatch:
    tag_name: str
    tag_type: str
    score: float


RULES: list[tuple[str, str, tuple[str, ...], float]] = [
    ("macro", "topic", ("economy", "growth", "gdp", "consumer", "retail sales"), 0.75),
    ("central_bank", "topic", ("fed", "federal reserve", "ecb", "rate cut", "rate hike"), 0.95),
    ("inflation", "topic", ("inflation", "cpi", "ppi", "consumer price index"), 0.95),
    ("commodities", "topic", ("gold", "oil", "crude", "commodity"), 0.8),
    ("equities", "topic", ("stocks", "equities", "shares", "s&p 500"), 0.7),
    ("bonds", "topic", ("bond", "treasury yield", "treasury", "yields"), 0.8),
    ("fx", "topic", ("dollar", "fx", "yen", "euro", "currency"), 0.75),
    ("geopolitics", "topic", ("tariff", "war", "sanction", "iran", "ukraine", "china trade"), 0.75),
    ("USD", "asset", ("dollar", "usd"), 0.8),
    ("UST", "asset", ("treasury", "treasuries", "bond yields"), 0.8),
    ("gold", "asset", ("gold",), 0.85),
    ("oil", "asset", ("oil", "crude"), 0.85),
    ("A_share", "asset", ("a-shares", "a shares", "shanghai", "shenzhen"), 0.7),
    ("ferrous_chain", "asset", ("iron ore", "steel", "rebar", "coal"), 0.75),
    ("United States", "region", ("fed", "federal reserve", "us ", "u.s.", "america", "treasury", "bls"), 0.85),
    ("China", "region", ("china", "pboc", "beijing"), 0.8),
    ("Europe", "region", ("europe", "euro zone", "ecb", "brussels", "germany"), 0.8),
    ("Global", "region", ("global", "world"), 0.65),
    ("data", "event_type", ("cpi", "ppi", "employment", "payrolls", "retail sales", "data"), 0.9),
    ("policy", "event_type", ("rate", "policy", "minutes", "statement", "meeting"), 0.85),
    ("breaking", "event_type", ("live", "breaking", "urgent"), 0.9),
    ("earnings", "event_type", ("earnings", "profit", "revenue"), 0.75),
    ("geopolitics", "event_type", ("war", "sanction", "tariff"), 0.8),
    ("regulation", "event_type", ("regulation", "regulator", "enforcement"), 0.8),
]


def infer_tags(title: str, clean_text: str) -> list[TagMatch]:
    haystack = f"{title} {clean_text}".lower()
    matches: dict[tuple[str, str], TagMatch] = {}
    for tag_name, tag_type, keywords, score in RULES:
        pattern = "|".join(re.escape(keyword) for keyword in keywords)
        if re.search(pattern, haystack):
            key = (tag_name, tag_type)
            existing = matches.get(key)
            if existing is None or score > existing.score:
                matches[key] = TagMatch(tag_name=tag_name, tag_type=tag_type, score=score)
    return list(matches.values())
