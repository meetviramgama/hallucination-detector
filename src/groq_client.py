"""
Groq API Client
---------------
Thin wrapper around Groq API.
Same interface used across all components:
generator, extractor, verifier, scorer.

Usage:
    Set GROQ_API_KEY in your .env file.
    Never hardcode the key in code.
"""

import os
import time
from dataclasses import dataclass
from typing import Optional
from groq import Groq, BadRequestError
from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMResponse:
    text:          str
    model:         str
    input_tokens:  int
    output_tokens: int
    latency_s:     float


def get_client() -> Groq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                api_key = st.secrets["GROQ_API_KEY"]
                os.environ["GROQ_API_KEY"] = api_key
        except Exception:
            pass

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Please configure it in your environment, Streamlit secrets, or via the app sidebar."
        )
    return Groq(api_key=api_key)


def generate(
    model:       str,
    prompt:      str,
    system:      Optional[str] = None,
    max_tokens:  int   = 1000,
    temperature: float = 0.0,
    json_mode:   bool  = False,
) -> LLMResponse:
    """
    Call Groq API and return text + metrics.

    Args:
        model       : Groq model name
        prompt      : user message
        system      : system prompt (optional)
        max_tokens  : max output tokens
        temperature : 0.0 = deterministic (best for extraction/verification)
        json_mode   : True = forces JSON output (for claim extraction)
    """
    client   = get_client()
    messages = []

    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    kwargs = dict(
        model       = model,
        messages    = messages,
        max_tokens  = max_tokens,
        temperature = temperature,
    )
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    start = time.time()
    try:
        response = client.chat.completions.create(**kwargs)
    except BadRequestError as e:
        # If Groq fails with json_validate_failed, retry cleanly without response_format
        if json_mode and "json_validate_failed" in str(e):
            kwargs.pop("response_format", None)
            response = client.chat.completions.create(**kwargs)
        else:
            raise e

    latency = time.time() - start

    usage = getattr(response, "usage", None)
    in_tok = getattr(usage, "prompt_tokens", 0) if usage else 0
    out_tok = getattr(usage, "completion_tokens", 0) if usage else 0

    content = ""
    if response.choices and len(response.choices) > 0:
        content = response.choices[0].message.content or ""

    return LLMResponse(
        text          = content,
        model         = model,
        input_tokens  = in_tok,
        output_tokens = out_tok,
        latency_s     = round(latency, 3),
    )


if __name__ == "__main__":
    print("Testing Groq client...")
    result = generate(
        model  = "openai/gpt-oss-20b",
        prompt = "What is 2+2? Answer in one word.",
    )
    print(f"Response:  {result.text}")
    print(f"Latency:   {result.latency_s}s")
    print(f"Tokens:    {result.input_tokens} in / {result.output_tokens} out")
