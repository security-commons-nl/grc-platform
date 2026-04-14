# Project Context

This is a python project using fastapi with sqlalchemy.
It is a microservices repo with workspaces: backend (backend), frontend (frontend).

The API has 132 routes. See .codesight/routes.md for the full route map with methods, paths, and tags.
The database has 36 models. See .codesight/schema.md for the full schema with fields, types, and relations.
The UI has 32 components. See .codesight/components.md for the full list with props.
Middleware includes: auth, validation.

High-impact files (most imported, changes here affect many other files):
- frontend\src\lib\hooks\use-api.ts (imported by 4 files)
- frontend\src\components\inrichten\step-card.tsx (imported by 1 files)
- frontend\src\components\ui\button.tsx (imported by 1 files)
- frontend\src\lib\auth.ts (imported by 1 files)
- frontend\src\lib\constants.ts (imported by 1 files)
- frontend\src\lib\api-types.ts (imported by 1 files)

Required environment variables (no defaults):
- AI_API_KEY (.env.example)
- LANGFUSE_HOST (.env.example)
- LANGFUSE_PUBLIC_KEY (.env.example)
- LANGFUSE_SECRET_KEY (.env.example)
- NEXT_PUBLIC_API_URL (frontend\src\lib\constants.ts)

Read .codesight/wiki/index.md for orientation (WHERE things live). Then read actual source files before implementing. Wiki articles are navigation aids, not implementation guides.
Read .codesight/CODESIGHT.md for the complete AI context map including all routes, schema, components, libraries, config, middleware, and dependency graph.
