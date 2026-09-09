from relationship_pipeline import analyze_all_candidates


results = analyze_all_candidates()

print("Total analyzed relationships:", len(results))


for i, result in enumerate(results[:10], start=1):

    print(f"\nRESULT {i}")

    print(
        "Fact A:",
        result["fact_a_id"]
    )

    print(
        "Fact B:",
        result["fact_b_id"]
    )

    print(
        "Entity:",
        result["entity_resolution"]["entity_relationship"]
    )

    print(
        "Relationship:",
        result["relationship"]["relationship_type"]
    )

    print(
        "Explanation:",
        result["relationship"]["explanation"]
    )

    print(
        "Confidence:",
        result["relationship"]["confidence"]
    )