import os
import json

from dotenv import load_dotenv
from mistralai.client import Mistral


load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")

client = Mistral(api_key=api_key)


text = """
Revenue for FY2024 was $100 million.

The company employed 5,000 people.
"""


response = client.chat.complete(
    model="ministral-8b-2512",
    messages=[
        {
            "role": "user",
            "content": f"""
You are a fact extraction system.

Extract meaningful numerical or semantic facts from the
following text.

Rules:
1. Only extract information explicitly supported by the text.
2. Never infer, assume, or guess missing information.
3. If a field is not explicitly stated, return null.
4. Every extracted fact must include its evidence.
5. The evidence must come directly from the provided text.

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
                                }
                            },
                            "required": [
                                "subject",
                                "property",
                                "value",
                                "unit",
                                "period",
                                "evidence"
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


result = json.loads(response.choices[0].message.content)
for fact in result["facts"]:
    print("\nFACT")
    print("Subject:", fact["subject"])
    print("Property:", fact["property"])
    print("Value:", fact["value"])
    print("Unit:", fact["unit"])
    print("Period:", fact["period"])
    print("Evidence:", fact["evidence"])
print(json.dumps(result, indent=2))
