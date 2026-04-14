# Evidence

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Evidence subsystem handles **3 routes** and touches: auth, db.

## Routes

- `GET` `/{evidence_id}` params(evidence_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\evidence.py`
- `PATCH` `/{evidence_id}` params(evidence_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\evidence.py`
- `DELETE` `/{evidence_id}` params(evidence_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\evidence.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `backend\app\api\v1\endpoints\evidence.py`

---
_Back to [overview.md](./overview.md)_