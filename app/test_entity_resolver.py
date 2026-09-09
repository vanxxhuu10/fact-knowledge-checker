from entity_resolver import resolve_entities


result = resolve_entities(
    "Northstar Logistics",
    "Revenue for FY2024 was $120 million.",
    "Northstar Logistics Limited",
    "The company reported revenue of $120 million for FY2024."
)

print("Relationship:", result["entity_relationship"])
print("Explanation:", result["explanation"])
print("Confidence:", result["confidence"])