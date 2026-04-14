# Documents

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Documents subsystem handles **15 routes** and touches: auth, db.

## Routes

- `GET` `/{document_id}` params(document_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\documents.py`
- `PATCH` `/{document_id}` params(document_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\documents.py`
- `DELETE` `/{document_id}` params(document_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\documents.py`
- `GET` `/versions/` → out: list [auth, db]
  `backend\app\api\v1\endpoints\documents.py`
- `GET` `/versions/{version_id}` params(version_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\documents.py`
- `GET` `/versions/{version_id}/export` params(version_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\documents.py`
- `POST` `/versions/` → in: DocumentCreate, out: list [auth, db]
  `backend\app\api\v1\endpoints\documents.py`
- `GET` `/input-documents/` → out: list [auth, db]
  `backend\app\api\v1\endpoints\documents.py`
- `GET` `/input-documents/{input_doc_id}` params(input_doc_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\documents.py`
- `POST` `/input-documents/` → in: DocumentCreate, out: list [auth, db]
  `backend\app\api\v1\endpoints\documents.py`
- `PATCH` `/input-documents/{input_doc_id}` params(input_doc_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\documents.py`
- `GET` `/gap-analysis/` → out: list [auth, db]
  `backend\app\api\v1\endpoints\documents.py`
- `GET` `/gap-analysis/{gap_id}` params(gap_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\documents.py`
- `POST` `/gap-analysis/` → in: DocumentCreate, out: list [auth, db]
  `backend\app\api\v1\endpoints\documents.py`
- `PATCH` `/gap-analysis/{gap_id}` params(gap_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\documents.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `backend\app\api\v1\endpoints\documents.py`

---
_Back to [overview.md](./overview.md)_