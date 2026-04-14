# Standards

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Standards subsystem handles **22 routes** and touches: auth, db.

## Routes

- `GET` `/{standard_id}` params(standard_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\standards.py`
- `PATCH` `/{standard_id}` params(standard_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\standards.py`
- `DELETE` `/{standard_id}` params(standard_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\standards.py`
- `GET` `/requirements/` → out: list [auth, db]
  `backend\app\api\v1\endpoints\standards.py`
- `GET` `/requirements/{requirement_id}` params(requirement_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\standards.py`
- `POST` `/requirements/` → in: StandardCreate, out: list [auth, db]
  `backend\app\api\v1\endpoints\standards.py`
- `PATCH` `/requirements/{requirement_id}` params(requirement_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\standards.py`
- `DELETE` `/requirements/{requirement_id}` params(requirement_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\standards.py`
- `GET` `/mappings/` → out: list [auth, db]
  `backend\app\api\v1\endpoints\standards.py`
- `GET` `/mappings/{mapping_id}` params(mapping_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\standards.py`
- `POST` `/mappings/` → in: StandardCreate, out: list [auth, db]
  `backend\app\api\v1\endpoints\standards.py`
- `PATCH` `/mappings/{mapping_id}` params(mapping_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\standards.py`
- `DELETE` `/mappings/{mapping_id}` params(mapping_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\standards.py`
- `GET` `/normenkader/` → out: list [auth, db]
  `backend\app\api\v1\endpoints\standards.py`
- `POST` `/normenkader/` → in: StandardCreate, out: list [auth, db]
  `backend\app\api\v1\endpoints\standards.py`
- `PATCH` `/normenkader/{nk_id}` params(nk_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\standards.py`
- `DELETE` `/normenkader/{nk_id}` params(nk_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\standards.py`
- `GET` `/ingestions/` → out: list [auth, db]
  `backend\app\api\v1\endpoints\standards.py`
- `GET` `/ingestions/{ingestion_id}` params(ingestion_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\standards.py`
- `POST` `/ingestions/` → in: StandardCreate, out: list [auth, db]
  `backend\app\api\v1\endpoints\standards.py`
- `PATCH` `/ingestions/{ingestion_id}` params(ingestion_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\standards.py`
- `DELETE` `/ingestions/{ingestion_id}` params(ingestion_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\standards.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `backend\app\api\v1\endpoints\standards.py`

---
_Back to [overview.md](./overview.md)_