
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

# Set an explicit HTTP timeout in milliseconds.
client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(timeout=30000),
)

GEMINI_MODELS = [
    "gemini-3.5-flash-lite",
    # "gemini-2.5-flash-lite",
]



def generate_response(prompt):

    last_error = None

    for model in GEMINI_MODELS:

        for attempt in range(2):

            start_time = time.perf_counter()

            try:
                print(
                    f"[Gemini] Trying {model}, "
                    f"attempt {attempt + 1}",
                    flush=True
                )

                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        max_output_tokens=800,
                        temperature=0.2,
                    ),
                )

                elapsed = time.perf_counter() - start_time

                print(
                    f"[Gemini] {model} succeeded in "
                    f"{elapsed:.2f}s",
                    flush=True
                )

                if not response.text:
                    raise RuntimeError(
                        f"{model} returned an empty response."
                    )

                return response.text

            except Exception as e:

                last_error = e
                elapsed = time.perf_counter() - start_time
                error_text = str(e).upper()

                print(
                    f"[Gemini] {model} failed after "
                    f"{elapsed:.2f}s: {e}",
                    flush=True
                )

                transient = any(
                    code in error_text
                    for code in [
                        "503",
                        "UNAVAILABLE",
                        "429",
                        "RESOURCE_EXHAUSTED",
                        "500",
                        "502",
                        "504",
                        "TIMEOUT",
                        "TIMED OUT",
                    ]
                )

                if transient:
                    if attempt == 0:
                        time.sleep(2)
                        continue

                    break

                raise RuntimeError(
                    f"Gemini request failed: {e}"
                ) from e

    raise RuntimeError(
        f"All Gemini models failed. Last error: {last_error}"
    )
