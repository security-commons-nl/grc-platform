# Risks

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Risks subsystem handles **6 routes** and touches: auth, db.

## Routes

- `GET` `/{risk_id}` params(risk_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\risks.py`
- `PATCH` `/{risk_id}` params(risk_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\risks.py`
- `DELETE` `/{risk_id}` params(risk_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\risks.py`
- `GET` `/links/` → out: list [auth, db]
  `backend\app\api\v1\endpoints\risks.py`
- `POST` `/links/` → in: RiskCreate, out: list [auth, db]
  `backend\app\api\v1\endpoints\risks.py`
- `DELETE` `/links/{risk_id}/{control_id}` params(risk_id, control_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\risks.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `backend\app\api\v1\endpoints\risks.py`

---
_Back to [overview.md](./overview.md)_