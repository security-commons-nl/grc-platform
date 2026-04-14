# Controls

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Controls subsystem handles **3 routes** and touches: auth, db.

## Routes

- `GET` `/{control_id}` params(control_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\controls.py`
- `PATCH` `/{control_id}` params(control_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\controls.py`
- `DELETE` `/{control_id}` params(control_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\controls.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `backend\app\api\v1\endpoints\controls.py`

---
_Back to [overview.md](./overview.md)_