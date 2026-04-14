# Incidents

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Incidents subsystem handles **3 routes** and touches: auth, db.

## Routes

- `GET` `/{incident_id}` params(incident_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\incidents.py`
- `PATCH` `/{incident_id}` params(incident_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\incidents.py`
- `DELETE` `/{incident_id}` params(incident_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\incidents.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `backend\app\api\v1\endpoints\incidents.py`

---
_Back to [overview.md](./overview.md)_