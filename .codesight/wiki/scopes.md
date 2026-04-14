# Scopes

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Scopes subsystem handles **3 routes** and touches: auth, db.

## Routes

- `GET` `/{scope_id}` params(scope_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\scopes.py`
- `PATCH` `/{scope_id}` params(scope_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\scopes.py`
- `DELETE` `/{scope_id}` params(scope_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\scopes.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `backend\app\api\v1\endpoints\scopes.py`

---
_Back to [overview.md](./overview.md)_