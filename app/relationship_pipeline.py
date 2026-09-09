from fact_matcher import get_candidate_pairs
from entity_resolution_cache import get_entity_resolution
from relationship_analyzer import analyze_relationship
from database import insert_relationship


def analyze_and_store_candidates(target_document_id=None):
    """Run entity resolution and relationship analysis across candidate pairs and persist to DB."""
    candidate_pairs = get_candidate_pairs(target_document_id=target_document_id)

    results = []

    for fact1, fact2 in candidate_pairs:
        # fact tuple format from DB: (id, document_id, subject, property, attributes, evidence_text, page_number, confidence)
        fact1_id, fact1_doc_id, subject1, prop1, attr1, evidence1, page1 = fact1[0], fact1[1], fact1[2], fact1[3], fact1[4], fact1[5], fact1[6]
        fact2_id, fact2_doc_id, subject2, prop2, attr2, evidence2, page2 = fact2[0], fact2[1], fact2[2], fact2[3], fact2[4], fact2[5], fact2[6]

        entity_result = get_entity_resolution(
            subject1,
            evidence1,
            subject2,
            evidence2
        )

        entity_relationship = entity_result.get("entity_relationship")

        # Filter: Only analyze facts if entities are comparable (same_entity or subentity)
        if entity_relationship not in ["same_entity", "subentity"]:
            continue

        normalized_fact1 = {
            "id": fact1_id,
            "document_id": fact1_doc_id,
            "subject": subject1,
            "property": prop1,
            "attributes": attr1,
            "evidence": {
                "text": evidence1,
                "page": page1
            }
        }

        normalized_fact2 = {
            "id": fact2_id,
            "document_id": fact2_doc_id,
            "subject": subject2,
            "property": prop2,
            "attributes": attr2,
            "evidence": {
                "text": evidence2,
                "page": page2
            }
        }

        relationship_result = analyze_relationship(
            normalized_fact1,
            normalized_fact2
        )

        rel_type = relationship_result.get("relationship_type", "contextual_difference")
        explanation = relationship_result.get("explanation", "")
        confidence = relationship_result.get("confidence", 1.0)

        # Persist relationship into PostgreSQL
        rel_id = insert_relationship(
            fact_a_id=fact1_id,
            fact_b_id=fact2_id,
            relationship_type=rel_type,
            explanation=explanation,
            confidence=confidence
        )

        results.append({
            "id": rel_id,
            "fact_a_id": fact1_id,
            "fact_b_id": fact2_id,
            "entity_resolution": entity_result,
            "relationship": relationship_result
        })

    return results


def analyze_all_candidates():
    """Alias for backwards compatibility."""
    return analyze_and_store_candidates()