# Scores

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Scores subsystem handles **15 routes** and touches: auth, db.

## Routes

- `GET` `/maturity-profiles/` → out: list [auth, db]
  `backend\app\api\v1\endpoints\scores.py`
- `GET` `/maturity-profiles/{profile_id}` params(profile_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\scores.py`
- `POST` `/maturity-profiles/` → in: MaturityProfileCreate, out: list [auth, db]
  `backend\app\api\v1\endpoints\scores.py`
- `PATCH` `/maturity-profiles/{profile_id}` params(profile_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\scores.py`
- `DELETE` `/maturity-profiles/{profile_id}` params(profile_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\scores.py`
- `GET` `/setup-scores/` → out: list [auth, db]
  `backend\app\api\v1\endpoints\scores.py`
- `GET` `/setup-scores/{score_id}` params(score_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\scores.py`
- `POST` `/setup-scores/` → in: MaturityProfileCreate, out: list [auth, db]
  `backend\app\api\v1\endpoints\scores.py`
- `PATCH` `/setup-scores/{score_id}` params(score_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\scores.py`
- `DELETE` `/setup-scores/{score_id}` params(score_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\scores.py`
- `GET` `/grc-scores/` → out: list [auth, db]
  `backend\app\api\v1\endpoints\scores.py`
- `GET` `/grc-scores/{score_id}` params(score_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\scores.py`
- `POST` `/grc-scores/` → in: MaturityProfileCreate, out: list [auth, db]
  `backend\app\api\v1\endpoints\scores.py`
- `PATCH` `/grc-scores/{score_id}` params(score_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\scores.py`
- `DELETE` `/grc-scores/{score_id}` params(score_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\scores.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `backend\app\api\v1\endpoints\scores.py`

---
_Back to [overview.md](./overview.md)_