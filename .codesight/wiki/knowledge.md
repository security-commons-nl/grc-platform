# Knowledge

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Knowledge subsystem handles **3 routes** and touches: auth, db.

## Routes

- `GET` `/{chunk_id}` params(chunk_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\knowledge.py`
- `PATCH` `/{chunk_id}` params(chunk_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\knowledge.py`
- `DELETE` `/{chunk_id}` params(chunk_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\knowledge.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `backend\app\api\v1\endpoints\knowledge.py`

---
_Back to [overview.md](./overview.md)_