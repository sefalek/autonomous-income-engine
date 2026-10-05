from __future__ import annotations
import html
import re
from dataclasses import dataclass, asdict
from urllib.parse import quote
import feedparser
import requests

@dataclass
class Signal:
    source: str
    title: str
    url: str
    summary: str = ''
    score_hint: float = 0.0

def clean(value: str) -> str:
    value = html.unescape(re.sub(r'<[^>]+>', ' ', value or ''))
    return re.sub(r'\s+', ' ', value).strip()

def google_news(topic: str) -> list[Signal]:
    url = 'https://news.google.com/rss/search?q=' + quote(topic) + '&hl=en-US&gl=US&ceid=US:en'
    feed = feedparser.parse(url)
    return [Signal('google_news', clean(e.get('title','')), e.get('link',''), clean(e.get('summary',''))) for e in feed.entries[:10]]

def hacker_news(topic: str) -> list[Signal]:
    try:
        r = requests.get('https://hn.algolia.com/api/v1/search', params={'query':topic,'tags':'story','hitsPerPage':10}, timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return []
    return [Signal('hacker_news', clean(x.get('title','')), x.get('url') or '', clean(x.get('story_text','')), float(x.get('points') or 0)) for x in data.get('hits',[])]

def reddit(topic: str) -> list[Signal]:
    try:
        r = requests.get('https://www.reddit.com/search.rss?q='+quote(topic)+'&sort=new', headers={'User-Agent':'autonomous-income-engine/0.1'}, timeout=20)
        r.raise_for_status()
        feed = feedparser.parse(r.text)
    except Exception:
        return []
    return [Signal('reddit', clean(e.get('title','')), e.get('link',''), clean(e.get('summary',''))) for e in feed.entries[:10]]

def collect(topics: list[str], max_candidates: int=30) -> list[dict]:
    signals=[]
    for topic in topics:
        signals += google_news(topic)
        signals += hacker_news(topic)
        signals += reddit(topic)
    seen=set()
    unique=[]
    for s in signals:
        key=re.sub(r'\W+','',s.title.lower())
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(asdict(s))
    return unique[:max_candidates]