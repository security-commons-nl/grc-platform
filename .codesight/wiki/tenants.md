# Tenants

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Tenants subsystem handles **19 routes** and touches: auth, db.

## Routes

- `GET` `/{tenant_id}` params(tenant_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\tenants.py`
- `PATCH` `/{tenant_id}` params(tenant_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\tenants.py`
- `DELETE` `/{tenant_id}` params(tenant_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\tenants.py`
- `GET` `/regions/` → out: list [auth, db]
  `backend\app\api\v1\endpoints\tenants.py`
- `GET` `/regions/{region_id}` params(region_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\tenants.py`
- `POST` `/regions/` → in: TenantCreate, out: list [auth, db]
  `backend\app\api\v1\endpoints\tenants.py`
- `PATCH` `/regions/{region_id}` params(region_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\tenants.py`
- `DELETE` `/regions/{region_id}` params(region_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\tenants.py`
- `GET` `/users/` → out: list [auth, db]
  `backend\app\api\v1\endpoints\tenants.py`
- `GET` `/users/{user_id}` params(user_id) → out: list [auth, db]
  `backend\app\api\v1\endpoints\tenants.py`
- `POST` `/users/` → in: TenantCreate, out: list [auth, db]
  `backend\app\api\v1\endpoints\tenants.py`
- `PATCH` `/users/{user_id}` params(user_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\tenants.py`
- `DELETE` `/users/{user_id}` params(user_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\tenants.py`
- `GET` `/user-tenant-roles/` → out: list [auth, db]
  `backend\app\api\v1\endpoints\tenants.py`
- `POST` `/user-tenant-roles/` → in: TenantCreate, out: list [auth, db]
  `backend\app\api\v1\endpoints\tenants.py`
- `DELETE` `/user-tenant-roles/{role_id}` params(role_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\tenants.py`
- `GET` `/user-region-roles/` → out: list [auth, db]
  `backend\app\api\v1\endpoints\tenants.py`
- `POST` `/user-region-roles/` → in: TenantCreate, out: list [auth, db]
  `backend\app\api\v1\endpoints\tenants.py`
- `DELETE` `/user-region-roles/{role_id}` params(role_id) → in: UUID, out: list [auth, db]
  `backend\app\api\v1\endpoints\tenants.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `backend\app\api\v1\endpoints\tenants.py`

---
_Back to [overview.md](./overview.md)_