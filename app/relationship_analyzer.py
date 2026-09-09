import os
import json
import time
import logging
from dotenv import load_dotenv
from mistralai.client import Mistral

load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)

logger = logging.getLogger("relationship_analyzer")


def analyze_relationship(fact1, fact2):
    """Analyze two candidate facts to classify relationship into corroboration, contradiction, or contextual_difference."""
    prompt = f"""
You are analyzing two facts extracted from different documents.

Determine the relationship between them.

Possible relationship types:

1. corroboration
   The two facts support the same underlying claim.

2. contradiction
   The two facts refer to the same underlying claim and context,
   but their values or meanings are incompatible.

3. contextual_difference
   The facts appear different or contradictory, but the difference
   can be explained by context such as:
   - time period / fiscal year / date
   - geographic scope
   - organizational scope / subentity
   - unit / measurement scale
   - measurement definition
   - other explicitly stated context

Rules:
- Use ONLY the information provided in the two facts and their evidence.
- Do not invent missing context.
- Do not assume two different values are contradictory if their
  periods, dates, scopes, units, or definitions differ.
- Choose exactly one primary relationship type.
- Do not describe a contextual_difference as corroboration or contradiction.
- If the facts have different values but explicitly refer to different
  periods, dates, scopes, units, or definitions, classify them as
  contextual_difference.
- Use corroboration only when both facts support the same claim under
  materially equivalent context.
- Use contradiction only when the facts refer to the same claim under
  materially equivalent context and their claims are incompatible.
- Explain why the selected relationship type is appropriate.
- Mention the specific contextual dimension responsible when using
  contextual_difference.
- The explanation must be concise and evidence-based.

FACT 1:
{json.dumps(fact1, indent=2)}

FACT 2:
{json.dumps(fact2, indent=2)}
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
                    "name": "relationship_analysis",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "relationship_type": {
                                "type": "string",
                                "enum": [
                                    "corroboration",
                                    "contradiction",
                                    "contextual_difference"
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
                            "relationship_type",
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
                logger.error(f"Relationship analysis failed: {e}")
                return {
                    "relationship_type": "contextual_difference",
                    "explanation": f"Unable to verify equivalency due to reasoning failure: {e}",
                    "confidence": 0.3
                }