# Fact Knowledge Layer — Document Grounding & Cross-Document Reasoning System

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![LLM Engine](https://img.shields.io/badge/LLM-Mistral%20AI-orange.svg)](https://mistral.ai/)
[![Database](https://img.shields.io/badge/database-Supabase%20PostgreSQL-3ECF8E.svg)](https://supabase.com/)

> **Superjoin VIT 2026 Engineering Intern Hiring Assignment**  
> *A document-grounded knowledge layer that extracts structured facts from PDFs, preserves source evidence, and reasons across documents to identify corroboration, contradiction, and contextual differences.*

---

## 1. Project Overview

Important facts are scattered across different documents. The same fact may be phrased differently, appear in multiple places, be supported by multiple pieces of evidence, contradict another document, or appear contradictory while actually referring to different time periods, scopes, or units.

This system solves this challenge by building a persistent, structured **Fact Knowledge Layer**. It:
1. Parses PDF text page-by-page while preserving exact source evidence quotes.
2. Uses structured LLM reasoning (**Mistral API**) to extract numerical and semantic facts without hallucinating.
3. Automatically deduplicates documents using **SHA-256 binary content hashing**.
4. Group candidate fact pairs using deterministic **canonical property mapping**.
5. Performs **4-way Entity Resolution** (`same_entity`, `subentity`, `different_entity`, `uncertain`).
6. Analyzes cross-document relationships into **Corroboration**, **Contradiction**, and **Contextual Difference**.
7. Persists grounded knowledge into **Supabase PostgreSQL** (`JSONB` dynamic attributes).
8. Exposes a clean **FastAPI REST API** and an interactive **Web Dashboard**.

---

## 2. Architecture & Pipeline Flow

```
                     PDF Upload
                         │
                         ▼
             SHA-256 Content Hashing
          (Duplicate Document Prevention)
                         │
                         ▼
             Page-Aware Text Extraction
                     (PyMuPDF)
                         │
                         ▼
              Fact Extraction (LLM)
             (Mistral Structured JSON)
                         │
                         ▼
              Fact Normalization &
             Evidence Grounding Link
                         │
                         ▼
              PostgreSQL JSONB Storage
                   (Facts Table)
                         │
                         ▼
                Candidate Generation
          (Canonical Semantic Matching)
                         │
                         ▼
                 Entity Resolution
            (Mistral 4-Way Classifier)
                         │
       ┌─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
   same_entity       subentity        uncertain / different
       │                 │
       └────────┬────────┘
                │
                ▼
      Relationship Analysis
            (Mistral)
                │
    ┌───────────┼───────────┐
    ▼           ▼           ▼
corroboration contradiction contextual_difference
    │           │           │
    └───────────┴───────────┘
                │
                ▼
      PostgreSQL Persistence
       (Relationships Table)
                │
                ▼
      FastAPI REST Endpoints
                │
                ▼
       Interactive Web UI
 (Dashboard / Evidence Grounding)
```

---

## 3. Mandatory Demo Cases

The system explicitly demonstrates all 4 required evaluation scenarios:

| Case | Relationship | Scenario | Demonstration |
|---|---|---|---|
| **Case 1** | `CORROBORATION` | Two documents express the same fact differently (e.g. `$120 million` vs `USD 120M` in `FY2024`). | Identifies both facts, verifies material equivalence, links evidence & page numbers. |
| **Case 2** | `CONTRADICTION` | Same entity, property, and period, but incompatible values (e.g. `4,800 employees` vs `6,200 employees` in `FY2024`). | Identifies conflict, marks contradiction, provides grounded explanation. |
| **Case 3** | `CONTEXTUAL DIFFERENCE` | Values differ because of contextual dimensions (e.g. `FY2023 $95M` vs `FY2024 $120M`). | Identifies time period variation, avoids false contradiction label, explains context. |
| **Case 4** | `UNCERTAINTY / FAILURE` | Ambiguous text where data is omitted or uncertain. | Returns `value = null` or `uncertain` entity/relationship with lower confidence score. |

---

## 4. Setup & Local Installation

### Step 1: Clone Repository & Create Virtual Environment
```bash
git clone https://github.com/vanxxhuu10/fact-knowledge-checker.git
cd fact-knowledge-checker

python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Create a `.env` file in the root directory:
```env
MISTRAL_API_KEY=your_mistral_api_key_here
DATABASE_URL=postgresql://user:password@host:port/dbname
```

> [!CAUTION]
> Never commit `.env` to GitHub. It is protected in `.gitignore`. A template file `.env.example` is included.

---

## 5. Running the Application

### Start API & Interactive Web Dashboard
```bash
python app/main.py
```
Or using Uvicorn directly:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Open your browser and navigate to:
```
http://localhost:8000
```

### Seed Synthetic Demo Datasets (4 Required Cases)
To populate the database with synthetic demo PDFs and run cross-document analysis:
```bash
python scripts/seed_demo.py
```

### Run Automated Unit & Integration Tests
```bash
pytest
```

---

## 6. API Endpoint Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/documents/upload` | Upload PDF file, extract page-grounded facts, and analyze relationships. |
| `GET` | `/api/documents` | List all ingested documents with fact counts. |
| `GET` | `/api/documents/{id}` | Retrieve single document info & extracted facts. |
| `GET` | `/api/facts` | Search/filter extracted facts across all documents. |
| `GET` | `/api/relationships` | List cross-document relationships (filter by `type`). |
| `GET` | `/api/relationships/{id}` | Detail view of relationship with side-by-side evidence quotes. |
| `POST` | `/api/analysis/run` | Run cross-document candidate matching & relationship analysis on demand. |
| `POST` | `/api/reset` | Truncate database tables for a fresh environment reset. |

---

## 7. Engineering Decisions & Architecture

### Separation of Deterministic Engineering & LLM Reasoning
- **Deterministic Code handles**: PDF parsing, SHA-256 hashing, page tracking, PostgreSQL persistence, JSON schema validation, canonical candidate generation, REST endpoints, UI rendering, rate-limit retries.
- **LLM handles**: Semantic fact extraction, verbatim evidence extraction, entity resolution, relationship reasoning, and natural language explanations.

### Key Engineering Decisions
1. **PostgreSQL `JSONB` for Flexible Schema**: Facts may contain different attributes (`value`, `unit`, `period`, `scope`, `geography`, `currency`). `JSONB` allows storing arbitrary key-value pairs without forcing rigid columns.
2. **Content Hashing (SHA-256)**: Computes binary file hash to prevent duplicate document ingestion on repeated uploads.
3. **Canonical Semantic Candidate Matching**: Normalizes properties (`employee count`, `number of employees`, `headcount` $\rightarrow$ `employee_count`) to filter candidate pairs deterministically. This prevents sending hundreds of irrelevant pairs to the LLM, avoiding HTTP 429 rate limit errors.
4. **4-Way Entity Resolution**: Distinguishes `same_entity` from `subentity` (e.g. *Northstar Logistics* vs *Northstar Logistics engineering organization*) to avoid false corroborations.

---

## 8. Tradeoffs & Limitations

### Tradeoffs
- **Deterministic Candidate Filtering vs Raw LLM Pairwise Matching**: Filtering by canonical property reduces LLM calls by >90%, making the system fast and cost-efficient, though un-mapped synonym pairs rely on token overlap rules.
- **JSONB Flexibility vs Rigid SQL Columns**: `JSONB` improves schema generality across arbitrary documents, though queries on specific attributes require JSON operators (`->>`).

### Limitations & Future Scope
- **Scanned PDFs / OCR**: PyMuPDF extracts text-based PDFs. Image-only scanned PDFs require an OCR pre-processing engine (e.g., Tesseract).
- **Large PDF Chunking**: Extremely large PDFs (100+ pages) benefit from page-sliding window chunking to maintain token window precision.

---

## 9. AI Tools Disclosure

- **LLM Provider**: Mistral API (`ministral-8b-2512`) used for fact extraction, entity resolution, and relationship classification.
- **Development Assistant**: Developed with assistance from Google Antigravity AI coding assistant.