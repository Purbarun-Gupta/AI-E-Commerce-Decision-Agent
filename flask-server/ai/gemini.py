import os
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)

GEMINI_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-2.5-flash-lite"
]


def generate_response(prompt):

    last_error = None

    for model in GEMINI_MODELS:

        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            return response.text

        except Exception as e:

            last_error = e

            if "503" in str(e) or "UNAVAILABLE" in str(e):
                time.sleep(1)
                continue

            raise

    raise RuntimeError(
        f"All Gemini models are currently unavailable. "
        f"Last error: {last_error}"
    )