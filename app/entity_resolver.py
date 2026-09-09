import os
import json
import time
import logging
from dotenv import load_dotenv
from mistralai.client import Mistral

load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)

logger = logging.getLogger("entity_resolver")


def resolve_entities(subject1, evidence1, subject2, evidence2):
    """Determine entity relationship (same_entity, subentity, different_entity, uncertain) using Mistral."""
    # Fast path: exact same string
    if subject1 and subject2 and subject1.strip().lower() == subject2.strip().lower():
        return {
            "entity_relationship": "same_entity",
            "explanation": f"Both subjects are identically named '{subject1}'.",
            "confidence": 0.98
        }

    prompt = f"""
Determine whether the two subjects refer to the same entity.

Use ONLY the subject names and evidence provided.

Possible results:

1. same_entity
   Both subjects refer to the same real-world entity.

2. subentity
   One subject refers to an organizational, functional, physical,
   or conceptual component of the other entity.

3. different_entity
   The subjects clearly refer to different entities with no
   relevant parent-child relationship.

4. uncertain
   There is not enough evidence to determine the relationship.

Important:
- A department, management group, engineering organization,
  fulfillment center, or platform can be a subentity/component
  rather than the same entity.
- Do not classify a component as same_entity merely because it
  shares the organization's name.
- Do not invent a parent-child relationship when the evidence
  does not support it.

Rules:
- Do not assume that similar names automatically mean the same entity.
- Do not assume that legal suffixes like "Limited", "Inc.", "Corp.", etc. automatically
  indicate a different entity if evidence shows they refer to the same corporate entity.
- Use the evidence to determine organizational scope when possible.
- If the evidence does not establish identity, use uncertain.

SUBJECT 1:
{subject1}

EVIDENCE 1:
{evidence1}

SUBJECT 2:
{subject2}

EVIDENCE 2:
{evidence2}
"""

    def _api_call():
        return client.chat.complete(
            model="ministral-8b-2512",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "entity_resolution",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "entity_relationship": {
                                "type": "string",
                                "enum": [
                                    "same_entity",
                                    "subentity",
                                    "different_entity",
                                    "uncertain"
                                ]
                            },
                            "explanation": {
                                "type": "string"
                            },
                            "confidence": {
                                "type": "number"
                            }
                        },
                        "required": [
                            "entity_relationship",
                            "explanation",
                            "confidence"
                        ],
                        "additionalProperties": False
                    }
                }
            }
        )

    for attempt in range(1, 4):
        try:
            response = _api_call()
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            if attempt < 3 and ("429" in str(e) or "capacity" in str(e)):
                time.sleep(2 * attempt)
            else:
                logger.error(f"Entity resolution failed: {e}")
                return {
                    "entity_relationship": "uncertain",
                    "explanation": f"API reasoning unavailable or uncertain: {e}",
                    "confidence": 0.3
                }