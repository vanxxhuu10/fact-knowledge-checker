import os
import psycopg
from psycopg.types.json import Jsonb
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg.connect(DATABASE_URL)


def init_db():
    """Ensure database schema is up-to-date."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                ALTER TABLE documents 
                ADD COLUMN IF NOT EXISTS file_hash TEXT UNIQUE;
                """
            )
        connection.commit()


# Run schema init on import
try:
    init_db()
except Exception as e:
    print(f"Database init warning: {e}")


def get_document_by_hash(file_hash):
    """Retrieve document by file content hash to prevent duplicate uploads."""
    if not file_hash:
        return None
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, filename, uploaded_at 
                FROM documents 
                WHERE file_hash = %s;
                """,
                (file_hash,)
            )
            row = cursor.fetchone()
            if row:
                return {"id": row[0], "filename": row[1], "uploaded_at": str(row[2])}
    return None


def insert_document(filename, file_hash=None):
    """Insert a new document record or return existing if hash matches."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            if file_hash:
                cursor.execute("SELECT id FROM documents WHERE file_hash = %s;", (file_hash,))
                existing_row = cursor.fetchone()
                if existing_row:
                    return existing_row[0]

                cursor.execute(
                    """
                    INSERT INTO documents (filename, file_hash)
                    VALUES (%s, %s)
                    ON CONFLICT (file_hash) DO UPDATE SET filename = EXCLUDED.filename
                    RETURNING id;
                    """,
                    (filename, file_hash)
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO documents (filename)
                    VALUES (%s)
                    RETURNING id;
                    """,
                    (filename,)
                )
            document_id = cursor.fetchone()[0]
        connection.commit()

    return document_id


def insert_fact(document_id, fact):
    """Insert an extracted fact into the database."""
    confidence = fact.get("confidence", 1.0)
    if confidence is None:
        confidence = 1.0

    attributes = fact.get("attributes", {})

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO facts (
                    document_id,
                    subject,
                    property,
                    attributes,
                    evidence_text,
                    page_number,
                    confidence
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (
                    document_id,
                    fact.get("subject") or "Unspecified Entity",
                    fact.get("property") or "unspecified_property",
                    Jsonb(attributes),
                    fact.get("evidence", {}).get("text", "") if isinstance(fact.get("evidence"), dict) else (fact.get("evidence") or ""),
                    fact.get("evidence", {}).get("page", 1) if isinstance(fact.get("evidence"), dict) else (fact.get("page_number") or 1),
                    confidence
                )
            )
            fact_id = cursor.fetchone()[0]
        connection.commit()

    return fact_id


def insert_relationship(fact_a_id, fact_b_id, relationship_type, explanation, confidence=1.0):
    """Insert a detected relationship between two facts."""
    if confidence is None:
        confidence = 1.0

    with get_connection() as connection:
        with connection.cursor() as cursor:
            # Check if relationship already exists
            cursor.execute(
                """
                SELECT id FROM relationships 
                WHERE (fact_a_id = %s AND fact_b_id = %s)
                   OR (fact_a_id = %s AND fact_b_id = %s);
                """,
                (fact_a_id, fact_b_id, fact_b_id, fact_a_id)
            )
            existing = cursor.fetchone()
            if existing:
                return existing[0]

            cursor.execute(
                """
                INSERT INTO relationships (
                    fact_a_id,
                    fact_b_id,
                    relationship_type,
                    explanation,
                    confidence
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (fact_a_id, fact_b_id, relationship_type, explanation, confidence)
            )
            relationship_id = cursor.fetchone()[0]
        connection.commit()

    return relationship_id


def get_all_documents():
    """Get list of all documents with fact counts."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT d.id, d.filename, d.file_hash, d.uploaded_at, COUNT(f.id) as fact_count
                FROM documents d
                LEFT JOIN facts f ON f.document_id = d.id
                GROUP BY d.id, d.filename, d.file_hash, d.uploaded_at
                ORDER BY d.id DESC;
                """
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": r[0],
                    "filename": r[1],
                    "file_hash": r[2],
                    "uploaded_at": str(r[3]),
                    "fact_count": r[4]
                }
                for r in rows
            ]


def get_document_facts(document_id):
    """Get all facts extracted for a document."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, document_id, subject, property, attributes, evidence_text, page_number, confidence, created_at
                FROM facts
                WHERE document_id = %s
                ORDER BY id ASC;
                """,
                (document_id,)
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": r[0],
                    "document_id": r[1],
                    "subject": r[2],
                    "property": r[3],
                    "attributes": r[4],
                    "evidence_text": r[5],
                    "page_number": r[6],
                    "confidence": r[7],
                    "created_at": str(r[8])
                }
                for r in rows
            ]


def get_all_facts():
    """Get all facts across all documents with document name."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT f.id, f.document_id, d.filename, f.subject, f.property, f.attributes, 
                       f.evidence_text, f.page_number, f.confidence, f.created_at
                FROM facts f
                JOIN documents d ON f.document_id = d.id
                ORDER BY f.id ASC;
                """
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": r[0],
                    "document_id": r[1],
                    "document_name": r[2],
                    "subject": r[3],
                    "property": r[4],
                    "attributes": r[5],
                    "evidence_text": r[6],
                    "page_number": r[7],
                    "confidence": r[8],
                    "created_at": str(r[9])
                }
                for r in rows
            ]


def get_all_relationships(relationship_type=None):
    """Get all stored relationships with full fact and document details."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            query = """
                SELECT 
                    r.id, r.relationship_type, r.explanation, r.confidence, r.created_at,
                    fa.id, fa.document_id, da.filename, fa.subject, fa.property, fa.attributes, fa.evidence_text, fa.page_number, fa.confidence,
                    fb.id, fb.document_id, db.filename, fb.subject, fb.property, fb.attributes, fb.evidence_text, fb.page_number, fb.confidence
                FROM relationships r
                JOIN facts fa ON r.fact_a_id = fa.id
                JOIN documents da ON fa.document_id = da.id
                JOIN facts fb ON r.fact_b_id = fb.id
                JOIN documents db ON fb.document_id = db.id
            """
            params = []
            if relationship_type:
                query += " WHERE r.relationship_type = %s"
                params.append(relationship_type)
            query += " ORDER BY r.id DESC;"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [
                {
                    "id": r[0],
                    "relationship_type": r[1],
                    "explanation": r[2],
                    "confidence": r[3],
                    "created_at": str(r[4]),
                    "fact_a": {
                        "id": r[5],
                        "document_id": r[6],
                        "document_name": r[7],
                        "subject": r[8],
                        "property": r[9],
                        "attributes": r[10],
                        "evidence_text": r[11],
                        "page_number": r[12],
                        "confidence": r[13]
                    },
                    "fact_b": {
                        "id": r[14],
                        "document_id": r[15],
                        "document_name": r[16],
                        "subject": r[17],
                        "property": r[18],
                        "attributes": r[19],
                        "evidence_text": r[20],
                        "page_number": r[21],
                        "confidence": r[22]
                    }
                }
                for r in rows
            ]


def reset_database():
    """Truncate all tables to start fresh."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE relationships, facts, documents RESTART IDENTITY CASCADE;")
        connection.commit()