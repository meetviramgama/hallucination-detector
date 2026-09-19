"""
Evidence Retriever
------------------
Retrieves evidence for claims using Wikipedia search API.
"""

import re
import time
import html
import requests
from dataclasses import dataclass

WIKI_API_URL = "https://en.wikipedia.org/w/api.php"


@dataclass
class Evidence:
    source:  str
    title:   str
    snippet: str
    url:     str


def _clean_search_query(claim: str) -> str:
    """
    Keep search query concise and focused for Wikipedia search API.
    """
    words = claim.split()
    if len(words) > 12:
        return " ".join(words[:12])
    return claim


def retrieve_evidence(claim: str) -> list:
    evidence_list = []
    if not claim or not claim.strip():
        return evidence_list

    search_query = _clean_search_query(claim.strip())

    params = {
        "action":      "query",
        "list":        "search",
        "srsearch":    search_query,
        "srlimit":     3,
        "format":      "json",
        "srprop":      "snippet",
    }

    headers = {
        "User-Agent": "HallucinationDetector/1.0 (https://github.com/example; contact@example.com)"
    }

    try:
        resp = requests.get(WIKI_API_URL, params=params, timeout=8, headers=headers)
        if resp.status_code == 429:
            # Brief backoff if rate limited
            time.sleep(0.5)
            resp = requests.get(WIKI_API_URL, params=params, timeout=8, headers=headers)

        if resp.status_code == 200:
            results = resp.json().get("query", {}).get("search", [])
            for r in results:
                title   = r.get("title", "")
                snippet = r.get("snippet", "")
                # Strip ALL HTML tags and unescape HTML entities
                snippet = re.sub(r"<[^>]+>", "", snippet)
                snippet = html.unescape(snippet).strip()
                url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
                if snippet:
                    evidence_list.append(Evidence(
                        source  = "wikipedia",
                        title   = title,
                        snippet = snippet,
                        url     = url,
                    ))
    except Exception as e:
        print(f"[retriever] Wikipedia error for '{search_query[:30]}': {e}")

    return evidence_list


def retrieve_evidence_batch(claims: list) -> dict:
    results = {}
    for claim in claims:
        results[claim] = retrieve_evidence(claim)
    return results


def format_evidence_for_verifier(evidence_list: list) -> str:
    if not evidence_list:
        return "No external evidence found for this claim."
    parts = []
    for i, ev in enumerate(evidence_list, 1):
        parts.append(f"Source {i} ({ev.source} — {ev.title}):\n{ev.snippet}")
    return "\n\n".join(parts)


if __name__ == "__main__":
    test_claims = [
        "The Eiffel Tower was built in 1887",
        "Paris is the capital of France",
    ]
    print("Testing evidence retriever...\n")
    for claim in test_claims:
        print(f"Claim: {claim}")
        evidence = retrieve_evidence(claim)
        print(f"Evidence found: {len(evidence)} sources")
        for ev in evidence:
            print(f"  [{ev.source}] {ev.title}: {ev.snippet[:100]}...")
        print()
