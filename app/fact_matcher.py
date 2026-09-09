from database import get_connection
from text_normalizer import are_properties_semantically_matching


def get_candidate_pairs(target_document_id=None):
    """Retrieve candidate fact pairs across different documents with semantically matching properties."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    document_id,
                    subject,
                    property,
                    attributes,
                    evidence_text,
                    page_number,
                    confidence
                FROM facts
                ORDER BY id;
                """
            )
            facts = cursor.fetchall()

    candidate_pairs = []

    for i in range(len(facts)):
        fact1 = facts[i]

        for j in range(i + 1, len(facts)):
            fact2 = facts[j]

            # Facts must come from different documents
            if fact1[1] == fact2[1]:
                continue

            # If target_document_id specified, at least one fact must belong to it
            if target_document_id is not None:
                if fact1[1] != target_document_id and fact2[1] != target_document_id:
                    continue

            property1 = fact1[3]
            property2 = fact2[3]

            # Check semantic property equivalence
            if not are_properties_semantically_matching(property1, property2):
                continue

            candidate_pairs.append((fact1, fact2))

    return candidate_pairs