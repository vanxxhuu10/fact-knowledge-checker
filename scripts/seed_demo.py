import os
import sys

# Add app directory to sys.path
sys.path.insert(0, os.path.abspath("app"))

from database import reset_database, get_all_documents, get_all_facts, get_all_relationships
from pipeline import process_pdf
from relationship_pipeline import analyze_and_store_candidates


def seed_demo_environment():
    """Reset DB, process all demo PDFs, and output grounding report."""
    print("==================================================")
    print("RESETTING DATABASE & INITIALIZING DEMO ENVIRONMENT")
    print("==================================================")
    reset_database()
    print("Database truncated cleanly.\n")

    demo_dir = os.path.abspath(r"data/demo")
    if not os.path.exists(demo_dir):
        print(f"Error: Demo directory {demo_dir} does not exist.")
        return

    pdf_files = sorted([f for f in os.listdir(demo_dir) if f.endswith(".pdf")])
    print(f"Found {len(pdf_files)} synthetic demo PDFs in data/demo:\n")

    for filename in pdf_files:
        pdf_path = os.path.join(demo_dir, filename)
        print(f" Processing: {filename} ...")
        res = process_pdf(pdf_path, auto_analyze=False)
        print(f"   Document ID: {res['document_id']} | Facts Extracted: {res['facts_extracted']}")

    print("\n--------------------------------------------------")
    print("RUNNING CROSS-DOCUMENT CANDIDATE MATCHING & ANALYSIS")
    print("--------------------------------------------------")
    relationships = analyze_and_store_candidates()
    print(f"Analysis complete. Total relationships stored: {len(relationships)}\n")

    print("==================================================")
    print("DEMO VERIFICATION SUMMARY REPORT")
    print("==================================================")
    docs = get_all_documents()
    facts = get_all_facts()
    stored_rels = get_all_relationships()

    print(f"Total Documents Ingested : {len(docs)}")
    print(f"Total Grounded Facts     : {len(facts)}")
    print(f"Total Relationships      : {len(stored_rels)}\n")

    # Group relationships by type
    rel_counts = {}
    for r in stored_rels:
        t = r["relationship_type"]
        rel_counts[t] = rel_counts.get(t, 0) + 1

    print("Relationship Type Breakdown:")
    for r_type, count in rel_counts.items():
        print(f"  - {r_type.upper()}: {count}")

    print("\n--------------------------------------------------")
    print("DETAILED RELATIONSHIPS & EVIDENCE GROUNDING")
    print("--------------------------------------------------")
    for idx, r in enumerate(stored_rels, 1):
        print(f"\n[RELATIONSHIP #{idx}] — {r['relationship_type'].upper()}")
        print(f" Explanation : {r['explanation']}")
        print(f" Confidence  : {r['confidence']}")
        
        fa = r['fact_a']
        fb = r['fact_b']
        print(f" Fact A: [{fa['document_name']} p.{fa['page_number']}] {fa['subject']} | {fa['property']} = {fa['attributes']}")
        print(f"         Evidence A: \"{fa['evidence_text']}\"")
        print(f" Fact B: [{fb['document_name']} p.{fb['page_number']}] {fb['subject']} | {fb['property']} = {fb['attributes']}")
        print(f"         Evidence B: \"{fb['evidence_text']}\"")

    print("\n==================================================")
    print("SEEDING COMPLETE — DEMO ENVIRONMENT READY!")
    print("==================================================")


if __name__ == "__main__":
    seed_demo_environment()
