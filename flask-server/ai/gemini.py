
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
                        max_output_tokens=500,
                        temperature=0.2,
                    ),
                )

                if not response.text:
                    raise RuntimeError("Empty Gemini response")

                print(
                    f"[Gemini] Success: "
                    f"{time.perf_counter() - start_time:.2f}s",
                    flush=True
                )

                return response.text

            except Exception as e:

                last_error = e
                error_text = str(e).upper()

                print(
                    f"[Gemini] Failed: {e}",
                    flush=True
                )

                transient = any(
                    code in error_text
                    for code in [
                        "503",
                        "UNAVAILABLE",
                        "504",
                        "DEADLINE_EXCEEDED",
                        "429",
                        "RESOURCE_EXHAUSTED",
                        "500",
                        "502",
                        "TIMEOUT",
                    ]
                )

                if transient:
                    if attempt == 0:
                        wait_time = 2 ** attempt
                        print(
                            f"[Gemini] Retrying in {wait_time}s",
                            flush=True
                        )
                        time.sleep(wait_time)
                        continue

                    break

                raise RuntimeError(
                    f"Gemini error with {model}: {e}"
                ) from e

    raise RuntimeError(
        f"All configured Gemini models failed. "
        f"Last error: {last_error}"
    )
