
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors

from prompts import PLANNER_PROMPT

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else None

MODEL_NAME = "gemini-3.5-flash-lite"
MAX_API_RETRIES = 3


def create_plan(question: str) -> list[str]:
    """Generate a reasoning plan using Gemini, with retries for temporary failures."""

    if client is None:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Check your .env file."
        )

    for attempt in range(MAX_API_RETRIES):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=(
                    f"{PLANNER_PROMPT}\n\n"
                    f"User question: {question}\n\n"
                    "Return only a numbered plan."
                ),
            )

            response_text = response.text or ""
            steps = []

            for line in response_text.splitlines():
                line = line.strip()

                if not line:
                    continue

                cleaned = line.lstrip("0123456789").lstrip(".):- ").strip()

                if cleaned:
                    steps.append(cleaned)

            if not steps:
                raise ValueError("Gemini returned an empty plan.")

            return steps

        except errors.APIError as exc:
            # Retry temporary server errors and rate limits.
            if exc.code not in (429, 500, 502, 503, 504):
                raise

            if attempt == MAX_API_RETRIES - 1:
                raise RuntimeError(
                    "Gemini is temporarily unavailable after 3 attempts. "
                    "Please try again later."
                ) from exc

            wait_seconds = 2 ** (attempt + 1)
            print(
                f"Gemini temporarily unavailable. "
                f"Retrying in {wait_seconds} seconds..."
            )
            time.sleep(wait_seconds)

    raise RuntimeError("Could not generate a plan.")
