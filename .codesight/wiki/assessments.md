# Assessments

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Assessments subsystem handles **13 routes** and touches: auth, db.

## Routes

- `GET` `/{assessment_id}` params(assessment_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\assessments.py`
- `PATCH` `/{assessment_id}` params(assessment_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\assessments.py`
- `DELETE` `/{assessment_id}` params(assessment_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\assessments.py`
- `GET` `/findings/` → out: list [auth, db]
  `backend\app\api\v1\endpoints\assessments.py`
- `GET` `/findings/{finding_id}` params(finding_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\assessments.py`
- `POST` `/findings/` → in: AssessmentCreate, out: list [auth, db]
  `backend\app\api\v1\endpoints\assessments.py`
- `PATCH` `/findings/{finding_id}` params(finding_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\assessments.py`
- `DELETE` `/findings/{finding_id}` params(finding_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\assessments.py`
- `GET` `/corrective-actions/` → out: list [auth, db]
  `backend\app\api\v1\endpoints\assessments.py`
- `GET` `/corrective-actions/{action_id}` params(action_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\assessments.py`
- `POST` `/corrective-actions/` → in: AssessmentCreate, out: list [auth, db]
  `backend\app\api\v1\endpoints\assessments.py`
- `PATCH` `/corrective-actions/{action_id}` params(action_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\assessments.py`
- `DELETE` `/corrective-actions/{action_id}` params(action_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\assessments.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `backend\app\api\v1\endpoints\assessments.py`

---
_Back to [overview.md](./overview.md)_