import os
import json
import time
import logging
from dotenv import load_dotenv
from mistralai.client import Mistral

load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)

logger = logging.getLogger("fact_extractor")


def call_mistral_with_retry(func, max_retries=3, initial_delay=2):
    """Wrapper to handle rate limiting (429) or transient errors with backoff."""
    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        try:
            return func()
        except Exception as e:
            err_msg = str(e).lower()
            if ("429" in err_msg or "capacity" in err_msg or "rate" in err_msg) and attempt < max_retries:
                logger.warning(f"Mistral API rate limit encountered (attempt {attempt}/{max_retries}). Retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2
            else:
                if attempt == max_retries:
                    logger.error(f"Mistral API failed after {max_retries} attempts: {e}")
                raise e


def extract_facts(text):
    """Extract structured facts with evidence and confidence from text chunk using Mistral."""
    if not text or not text.strip():
        return []

    def _api_call():
        return client.chat.complete(
            model="ministral-8b-2512",
            messages=[
                {
                    "role": "user",
                    "content": f"""
You are a document-grounded fact extraction system.

Extract all meaningful numerical, semantic, or operational facts from the provided text.

Rules:
1. Only extract information explicitly supported by the text.
2. Never infer, assume, or guess missing information.
3. If a field (e.g. value, unit, period) is missing or ambiguous, return null.
4. Every extracted fact MUST include verbatim evidence text quoted directly from the input text.
5. Provide a confidence score between 0.0 and 1.0 for each fact based on textual clarity.

TEXT:
{text}
"""
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "fact_extraction",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "facts": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "subject": {
                                            "type": ["string", "null"]
                                        },
                                        "property": {
                                            "type": ["string", "null"]
                                        },
                                        "value": {
                                            "type": ["string", "number", "null"]
                                        },
                                        "unit": {
                                            "type": ["string", "null"]
                                        },
                                        "period": {
                                            "type": ["string", "null"]
                                        },
                                        "evidence": {
                                            "type": ["string", "null"]
                                        },
                                        "confidence": {
                                            "type": ["number", "null"]
                                        }
                                    },
                                    "required": [
                                        "subject",
                                        "property",
                                        "value",
                                        "unit",
                                        "period",
                                        "evidence",
                                        "confidence"
                                    ],
                                    "additionalProperties": False
                                }
                            }
                        },
                        "required": ["facts"],
                        "additionalProperties": False
                    }
                }
            }
        )

    try:
        response = call_mistral_with_retry(_api_call)
        result = json.loads(response.choices[0].message.content)
        return result.get("facts", [])
    except Exception as e:
        logger.error(f"Error during fact extraction: {e}")
        return []