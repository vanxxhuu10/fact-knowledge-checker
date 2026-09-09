from entity_resolver import resolve_entities


subject_pairs = [
    (
        "Northstar Logistics",
        "Northstar Logistics Limited"
    ),
    (
        "Northstar Logistics",
        "Northstar Logistics management"
    ),
    (
        "Northstar Logistics Limited",
        "Northstar Logistics engineering organization"
    )
]


for subject1, subject2 in subject_pairs:

    result = resolve_entities(
        subject1,
        f"References to {subject1} in the documents.",
        subject2,
        f"References to {subject2} in the documents."
    )

    print("\n--------------------------------")
    print("SUBJECT 1:", subject1)
    print("SUBJECT 2:", subject2)
    print("RESULT:", result["entity_relationship"])
    print("EXPLANATION:", result["explanation"])
    print("CONFIDENCE:", result["confidence"])