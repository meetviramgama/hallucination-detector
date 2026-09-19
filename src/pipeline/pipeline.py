"""
Main Pipeline
-------------
Wires all components together in the correct order:

    User query
        ↓
    Generator (llama-3.1-8b) → full answer
        ↓
    Claim Extractor (llama-3.1-8b) → list of claims
        ↓
    Evidence Retriever (Wikipedia) → evidence per claim
        ↓
    Claim Verifier (llama-3.1-8b) → VERIFIED/FALSE/UNVERIFIED per claim
        ↓
    Trust Scorer → overall score 0-100
        ↓
    Return: answer + verified claims + trust score

Run:
    PYTHONPATH=src python3 src/pipeline/pipeline.py
"""

import sys
import time
from pathlib import Path
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).parent.parent))

from groq_client import generate
from extractor.claim_extractor import extract_claims_with_meta
from retriever.evidence_retriever import retrieve_evidence_batch
from verifier.claim_verifier import verify_claims_batch, VerificationResult
from scorer.trust_scorer import compute_trust_score, TrustScore

GENERATOR_MODEL = "openai/gpt-oss-20b"


@dataclass
class PipelineResponse:
    query:            str
    answer:           str
    claims:           list          # list of VerificationResult
    trust_score:      TrustScore
    generator_s:      float
    extractor_s:      float
    retriever_s:      float
    verifier_s:       float
    total_s:          float
    input_tokens:     int
    output_tokens:    int


def run(query: str) -> PipelineResponse:
    """
    Run the full hallucination detection pipeline.

    Args:
        query: user question

    Returns:
        PipelineResponse with answer, verified claims, and trust score
    """
    start         = time.time()
    total_in_tok  = 0
    total_out_tok = 0

    # ── Step 1: Generate answer ───────────────────────────────────────────
    gen_start = time.time()
    gen_resp  = generate(
        model       = GENERATOR_MODEL,
        prompt      = query,
        system      = "You are a helpful assistant. Answer clearly and thoroughly.",
        max_tokens  = 1000,
        temperature = 0.7,
    )
    generator_s    = time.time() - gen_start
    total_in_tok  += gen_resp.input_tokens
    total_out_tok += gen_resp.output_tokens
    answer         = gen_resp.text

    # ── Step 2: Extract claims ────────────────────────────────────────────
    ext_start  = time.time()
    ext_result = extract_claims_with_meta(answer)
    extractor_s    = time.time() - ext_start
    total_in_tok  += ext_result["input_tokens"]
    total_out_tok += ext_result["output_tokens"]
    claims_text    = ext_result["claims"]

    # ── Step 3: Retrieve evidence ─────────────────────────────────────────
    ret_start            = time.time()
    claims_with_evidence = retrieve_evidence_batch(claims_text)
    retriever_s          = time.time() - ret_start

    # ── Step 4: Verify claims ─────────────────────────────────────────────
    ver_start  = time.time()
    results    = verify_claims_batch(claims_with_evidence)
    verifier_s = time.time() - ver_start

    # ── Step 5: Compute trust score ───────────────────────────────────────
    trust = compute_trust_score(results)

    total_s = time.time() - start

    return PipelineResponse(
        query         = query,
        answer        = answer,
        claims        = results,
        trust_score   = trust,
        generator_s   = round(generator_s, 2),
        extractor_s   = round(extractor_s, 2),
        retriever_s   = round(retriever_s, 2),
        verifier_s    = round(verifier_s, 2),
        total_s       = round(total_s, 2),
        input_tokens  = total_in_tok,
        output_tokens = total_out_tok,
    )


if __name__ == "__main__":
    test_query = "Tell me about the Eiffel Tower — when was it built and how tall is it?"

    print("\n" + "="*70)
    print("HALLUCINATION DETECTOR — PIPELINE SMOKE TEST")
    print("="*70)
    print(f"Query: {test_query}\n")

    result = run(test_query)

    print(f"Answer:\n{result.answer}\n")
    print(f"{'='*70}")
    print(f"Claims found: {len(result.claims)}")
    print()

    ICONS = {"VERIFIED": "✓", "FALSE": "✗", "UNVERIFIED": "?"}

    for r in result.claims:
        icon = ICONS.get(r.verdict, "?")
        print(f"  {icon} [{r.verdict}] {r.claim}")
        print(f"     Confidence: {r.confidence:.0%}")
        print(f"     Reasoning:  {r.reasoning}")
        print()

    print(f"{'='*70}")
    print(f"Trust Score:  {result.trust_score.score}/100 — {result.trust_score.label}")
    print(f"Explanation:  {result.trust_score.explanation}")
    print(f"{'='*70}")
    print(f"Timing:")
    print(f"  Generate:  {result.generator_s}s")
    print(f"  Extract:   {result.extractor_s}s")
    print(f"  Retrieve:  {result.retriever_s}s")
    print(f"  Verify:    {result.verifier_s}s")
    print(f"  Total:     {result.total_s}s")
    print(f"Tokens:  {result.input_tokens} in / {result.output_tokens} out")
