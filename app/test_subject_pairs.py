from fact_matcher import get_candidate_pairs


pairs = get_candidate_pairs()

subject_pairs = set()

for fact1, fact2 in pairs:

    subject1 = fact1[2]
    subject2 = fact2[2]

    if subject1 == subject2:
        continue

    pair = tuple(sorted([subject1, subject2]))

    subject_pairs.add(pair)


print("Candidate fact pairs:", len(pairs))
print("Unique subject pairs:", len(subject_pairs))

print("\nSUBJECT PAIRS:")

for subject1, subject2 in sorted(subject_pairs):

    print(f"{subject1}  <->  {subject2}")