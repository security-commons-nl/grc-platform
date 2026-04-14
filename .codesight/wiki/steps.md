# Steps

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Steps subsystem handles **15 routes** and touches: auth, db.

## Routes

- `GET` `/{step_id}` params(step_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\steps.py`
- `PATCH` `/{step_id}` params(step_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\steps.py`
- `DELETE` `/{step_id}` params(step_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\steps.py`
- `GET` `/dependencies/` → out: list [auth, db]
  `backend\app\api\v1\endpoints\steps.py`
- `POST` `/dependencies/` → in: StepCreate, out: list [auth, db]
  `backend\app\api\v1\endpoints\steps.py`
- `DELETE` `/dependencies/{dep_id}` params(dep_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\steps.py`
- `GET` `/executions/` → out: list [auth, db]
  `backend\app\api\v1\endpoints\steps.py`
- `GET` `/executions/{execution_id}` params(execution_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\steps.py`
- `POST` `/executions/` → in: StepCreate, out: list [auth, db]
  `backend\app\api\v1\endpoints\steps.py`
- `PATCH` `/executions/{execution_id}` params(execution_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\steps.py`
- `DELETE` `/executions/{execution_id}` params(execution_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\steps.py`
- `GET` `/executions/{execution_id}/readiness` params(execution_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\steps.py`
- `GET` `/executions/{execution_id}/fulfillments` params(execution_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\steps.py`
- `POST` `/executions/{execution_id}/fulfillments` params(execution_id) → in: StepCreate, out: list [auth, db]
  `backend\app\api\v1\endpoints\steps.py`
- `DELETE` `/fulfillments/{fulfillment_id}` params(fulfillment_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\steps.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `backend\app\api\v1\endpoints\steps.py`

---
_Back to [overview.md](./overview.md)_