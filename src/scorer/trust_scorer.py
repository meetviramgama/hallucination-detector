"""
Trust Scorer
------------
Computes an overall trust score (0-100) for an LLM answer
based on individual claim verification results.

Score interpretation:
  90-100  Very trustworthy — all claims verified
  70-89   Mostly trustworthy — minor unverified claims
  50-69   Use with caution — some unverified claims
  20-49   Likely hallucination — false claims detected
  0-19    Do not trust — multiple false claims
"""

import sys
from pathlib import Path
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).parent.parent))
from verifier.claim_verifier import VerificationResult


@dataclass
class TrustScore:
    score:            int      # 0-100
    label:            str      # Very Trustworthy / Trustworthy / Caution / Unreliable / False
    total_claims:     int
    verified_count:   int
    false_count:      int
    unverified_count: int
    explanation:      str


def compute_trust_score(results: list) -> TrustScore:
    """
    Compute overall trust score from a list of VerificationResult objects.

    Scoring logic:
      Start at 100
      Each FALSE claim   : -30 points (weighted by confidence)
      Each UNVERIFIED    : -10 points
      Each VERIFIED      : +0 (baseline, no penalty)
      Minimum score      : 0

    Args:
        results: list of VerificationResult objects

    Returns:
        TrustScore with score, label, and breakdown
    """
    if not results:
        return TrustScore(
            score            = 100,
            label            = "No Claims",
            total_claims     = 0,
            verified_count   = 0,
            false_count      = 0,
            unverified_count = 0,
            explanation      = "No verifiable claims found in the answer.",
        )

    total       = len(results)
    verified    = [r for r in results if r.verdict == "VERIFIED"]
    false_items = [r for r in results if r.verdict == "FALSE"]
    unverified  = [r for r in results if r.verdict == "UNVERIFIED"]

    # Start at 100, subtract penalties
    score = 100

    for r in false_items:
        penalty = int(30 * r.confidence)   # higher confidence = bigger penalty
        score  -= penalty

    for r in unverified:
        score -= 10

    score = max(0, min(100, score))

    # Label
    if score >= 90:
        label = "Very Trustworthy"
    elif score >= 70:
        label = "Trustworthy"
    elif score >= 50:
        label = "Use With Caution"
    elif score >= 20:
        label = "Likely Hallucination"
    else:
        label = "Do Not Trust"

    # Explanation
    parts = []
    if verified:
        parts.append(f"{len(verified)} claim(s) verified")
    if false_items:
        parts.append(f"{len(false_items)} claim(s) found false")
    if unverified:
        parts.append(f"{len(unverified)} claim(s) could not be verified")
    explanation = " | ".join(parts) if parts else "No claims to evaluate"

    return TrustScore(
        score            = score,
        label            = label,
        total_claims     = total,
        verified_count   = len(verified),
        false_count      = len(false_items),
        unverified_count = len(unverified),
        explanation      = explanation,
    )


if __name__ == "__main__":
    # Simulate verification results to test scorer
    from verifier.claim_verifier import VerificationResult

    mock_results = [
        VerificationResult("Paris is the capital of France",   "VERIFIED",   0.99, "Wikipedia confirms"),
        VerificationResult("Eiffel Tower built in 1887",       "FALSE",      0.90, "Wikipedia says 1889"),
        VerificationResult("France population is 68 million",  "UNVERIFIED", 0.50, "No direct evidence"),
        VerificationResult("French Revolution began in 1789",  "VERIFIED",   0.95, "Wikipedia confirms"),
    ]

    score = compute_trust_score(mock_results)

    print("Trust Score Test\n" + "="*40)
    print(f"Score:       {score.score}/100")
    print(f"Label:       {score.label}")
    print(f"Total:       {score.total_claims} claims")
    print(f"Verified:    {score.verified_count}")
    print(f"False:       {score.false_count}")
    print(f"Unverified:  {score.unverified_count}")
    print(f"Explanation: {score.explanation}")
