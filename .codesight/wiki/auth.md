# Auth

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Auth subsystem handles **3 routes** and touches: auth.

## Routes

- `POST` `/dev-token` → in: DevTokenRequest, out: TokenResponse [auth]
  `backend\app\api\v1\endpoints\auth.py`
- `POST` `/agent-token` → in: DevTokenRequest, out: TokenResponse [auth]
  `backend\app\api\v1\endpoints\auth.py`
- `GET` `/me` → in: CurrentUse, out: TokenResponse [auth]
  `backend\app\api\v1\endpoints\auth.py`

## Middleware

- **auth** (auth) — `backend\app\api\v1\endpoints\auth.py`
- **auth** (auth) — `backend\app\core\auth.py`
- **auth.spec** (auth) — `frontend\e2e\auth.spec.ts`
- **auth** (auth) — `frontend\src\lib\auth.ts`
- **auth-provider** (auth) — `frontend\src\providers\auth-provider.tsx`

## Source Files

Read these before implementing or modifying this subsystem:
- `backend\app\api\v1\endpoints\auth.py`

---
_Back to [overview.md](./overview.md)_