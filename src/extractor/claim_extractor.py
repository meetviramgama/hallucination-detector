"""
Claim Extractor
---------------
Extracts individual verifiable factual claims from an LLM answer.

Each claim must be:
  - A single standalone factual statement
  - Independently verifiable against external sources
  - Specific (not vague opinions or predictions)

Example:
  Input:  "Paris is the capital of France. The Eiffel Tower
           was built in 1887 and stands 330 metres tall."

  Output: [
    "Paris is the capital of France",
    "The Eiffel Tower was built in 1887",
    "The Eiffel Tower stands 330 metres tall"
  ]
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from groq_client import generate

EXTRACTOR_MODEL = "openai/gpt-oss-20b"

EXTRACTOR_SYSTEM = """You are a precise claim extraction system.

Extract every individual factual claim from the given text.

Rules:
1. Each claim must be ONE standalone sentence
2. Each claim must be independently verifiable
3. Do NOT include opinions, predictions, or vague statements
4. Do NOT include the same fact twice
5. Keep claims specific — include numbers, names, dates exactly as stated
6. Skip any claim that cannot be checked against an external source

Output valid JSON only:
{
  "claims": [
    "claim one here",
    "claim two here"
  ]
}

No explanation. No markdown. JSON only."""


def _parse_claims_from_text(raw_text: str) -> list:
    """
    Robust parser for claim extraction JSON or list formats.
    """
    if not raw_text or not raw_text.strip():
        return []

    text = raw_text.strip()

    # 1. Direct JSON parse
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "claims" in data:
            return [str(c).strip() for c in data["claims"] if str(c).strip()]
        if isinstance(data, list):
            return [str(c).strip() for c in data if str(c).strip()]
    except Exception:
        pass

    # 2. Search for JSON object block
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            data = json.loads(match.group(0))
            if isinstance(data, dict) and "claims" in data:
                return [str(c).strip() for c in data["claims"] if str(c).strip()]
        except Exception:
            pass

    # 3. Fallback: Parse markdown / bullet points / numbered lines
    claims = []
    for line in text.split("\n"):
        line = line.strip()
        cleaned = re.sub(r'^(?:[\d]+[\.\)]|\-|\*)\s*', '', line).strip('"\'` ')
        if cleaned and len(cleaned) > 5 and not cleaned.startswith("{") and not cleaned.startswith("}") and "claims" not in cleaned.lower():
            claims.append(cleaned)

    return claims


def extract_claims(answer: str) -> list:
    """
    Extract verifiable factual claims from an LLM answer.

    Args:
        answer: the LLM generated answer text

    Returns:
        list of claim strings
    """
    if not answer.strip():
        return []

    response = generate(
        model      = EXTRACTOR_MODEL,
        prompt     = f"Extract all factual claims from this text:\n\n{answer}",
        system     = EXTRACTOR_SYSTEM,
        max_tokens = 2000,
        json_mode  = True,
    )

    return _parse_claims_from_text(response.text)


def extract_claims_with_meta(answer: str) -> dict:
    """
    Same as extract_claims() but also returns timing metadata.
    Used by the eval harness and pipeline.
    """
    if not answer.strip():
        return {
            "claims":        [],
            "latency_s":     0.0,
            "input_tokens":  0,
            "output_tokens": 0,
        }

    response = generate(
        model      = EXTRACTOR_MODEL,
        prompt     = f"Extract all factual claims from this text:\n\n{answer}",
        system     = EXTRACTOR_SYSTEM,
        max_tokens = 2000,
        json_mode  = True,
    )

    claims = _parse_claims_from_text(response.text)

    return {
        "claims":        claims,
        "latency_s":     response.latency_s,
        "input_tokens":  response.input_tokens,
        "output_tokens": response.output_tokens,
    }


if __name__ == "__main__":
    test_answer = """
    Paris is the capital of France and has a population of about 2.1 million people.
    The Eiffel Tower was built in 1889 and stands 330 metres tall.
    France is a member of the European Union and uses the Euro as its currency.
    The French Revolution began in 1789.
    """

    print("Testing claim extractor...")
    print(f"\nInput:\n{test_answer.strip()}\n")

    result = extract_claims_with_meta(test_answer)

    print(f"Claims extracted: {len(result['claims'])}")
    for i, claim in enumerate(result["claims"], 1):
        print(f"  {i}. {claim}")

    print(f"\nLatency:  {result['latency_s']}s")
    print(f"Tokens:   {result['input_tokens']} in / {result['output_tokens']} out")