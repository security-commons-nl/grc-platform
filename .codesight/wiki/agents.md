# Agents

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Agents subsystem handles **5 routes** and touches: auth, db.

## Routes

- `POST` `/{agent_name}/conversations` params(agent_name) → out: ConversationResponse [auth, db]
  `backend\app\api\v1\endpoints\agents.py`
- `GET` `/conversations/{conversation_id}` params(conversation_id) → in: UUID, out: ConversationResponse [auth, db]
  `backend\app\api\v1\endpoints\agents.py`
- `POST` `/conversations/{conversation_id}/messages` params(conversation_id) → out: ConversationResponse [auth, db]
  `backend\app\api\v1\endpoints\agents.py`
- `POST` `/conversations/{conversation_id}/feedback` params(conversation_id) → out: ConversationResponse [auth, db]
  `backend\app\api\v1\endpoints\agents.py`
- `POST` `/conversations/{conversation_id}/generate` params(conversation_id) → out: ConversationResponse [auth, db]
  `backend\app\api\v1\endpoints\agents.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `backend\app\api\v1\endpoints\agents.py`

---
_Back to [overview.md](./overview.md)_