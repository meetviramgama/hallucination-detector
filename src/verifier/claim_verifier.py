"""
Claim Verifier
--------------
Verifies each extracted claim against retrieved external evidence.
Verdict: VERIFIED / FALSE / UNVERIFIED
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).parent.parent))
from groq_client import generate
from retriever.evidence_retriever import Evidence, format_evidence_for_verifier

VERIFIER_MODEL = "openai/gpt-oss-20b"

VERIFIER_SYSTEM = """You are a fact-checking system.

Given a claim and external evidence, decide if the evidence SUPPORTS, CONTRADICTS, or is SILENT on the claim.

Rules:
- Use ONLY the provided evidence — do NOT use your own memory
- If evidence clearly confirms → reply VERIFIED
- If evidence clearly contradicts → reply FALSE
- If evidence is silent or unclear → reply UNVERIFIED

Reply in this exact format:
VERDICT: [VERIFIED or FALSE or UNVERIFIED]
CONFIDENCE: [0.0 to 1.0]
REASONING: [one sentence]"""


@dataclass
class VerificationResult:
    claim:      str
    verdict:    str
    confidence: float
    reasoning:  str
    evidence:   list = field(default_factory=list)
    latency_s:  float = 0.0


def verify_claim(claim: str, evidence_list: list) -> VerificationResult:
    evidence_text = format_evidence_for_verifier(evidence_list)

    prompt = f"""Claim to verify:
"{claim}"

Evidence:
{evidence_text}

Based ONLY on the evidence above — is the claim VERIFIED, FALSE, or UNVERIFIED?"""

    response = generate(
        model      = VERIFIER_MODEL,
        prompt     = prompt,
        system     = VERIFIER_SYSTEM,
        max_tokens = 200,
        json_mode  = False,
    )

    # Parse plain text response
    text       = response.text.strip()
    verdict    = "UNVERIFIED"
    confidence = 0.5
    reasoning  = ""

    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("VERDICT:"):
            v = line.replace("VERDICT:", "").strip().upper()
            if v in {"VERIFIED", "FALSE", "UNVERIFIED"}:
                verdict = v
        elif line.startswith("CONFIDENCE:"):
            try:
                confidence = float(line.replace("CONFIDENCE:", "").strip())
            except ValueError:
                pass
        elif line.startswith("REASONING:"):
            reasoning = line.replace("REASONING:", "").strip()

    return VerificationResult(
        claim      = claim,
        verdict    = verdict,
        confidence = confidence,
        reasoning  = reasoning,
        evidence   = evidence_list,
        latency_s  = response.latency_s,
    )


def verify_claims_batch(claims_with_evidence: dict) -> list:
    return [
        verify_claim(claim, evidence)
        for claim, evidence in claims_with_evidence.items()
    ]


if __name__ == "__main__":
    from retriever.evidence_retriever import retrieve_evidence

    test_claims = [
        "The Eiffel Tower was built in 1887",
        "Paris is the capital of France",
        "France invented the internet",
    ]

    print("Testing claim verifier...\n" + "="*60)

    for claim in test_claims:
        print(f"Claim:      {claim}")
        evidence = retrieve_evidence(claim)
        result   = verify_claim(claim, evidence)
        print(f"Verdict:    {result.verdict}")
        print(f"Confidence: {result.confidence:.0%}")
        print(f"Reasoning:  {result.reasoning}")
        print(f"Latency:    {result.latency_s}s")
        print("="*60)
