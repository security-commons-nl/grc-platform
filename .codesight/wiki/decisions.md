# Decisions

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Decisions subsystem handles **1 routes** and touches: auth, db.

## Routes

- `GET` `/{decision_id}` params(decision_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\decisions.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `backend\app\api\v1\endpoints\decisions.py`

---
_Back to [overview.md](./overview.md)_