from fact_matcher import get_candidate_pairs

pairs = get_candidate_pairs()

print("Total candidate pairs:", len(pairs))

for fact1, fact2 in pairs[:20]:
    print("\n-----------------------------")

    print("FACT 1")
    print("Subject:", fact1[2])
    print("Property:", fact1[3])
    print("Attributes:", fact1[4])

    print("\nFACT 2")
    print("Subject:", fact2[2])
    print("Property:", fact2[3])
    print("Attributes:", fact2[4])