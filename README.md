# Local Permissioned AI Agent (Openclaw-Style)

This repo provides a minimal, local-first AI agent skeleton that **requires explicit user permission** before it can open apps or perform tasks. It is designed for privacy: you can grant one-time or persistent access per app, and revoke access at any time.

## Features
- Explicit permission prompts before the agent opens an app or executes a task.
- A local permissions store (`permissions.json`) you control.
- Simple CLI for testing tasks, granting, and revoking permissions.
- Extensible task registry (add new tasks safely).

## Quick start
```bash
python agent.py list-tasks
python agent.py run-task "draft_email"
python agent.py grant "mail"
python agent.py revoke "mail"
```

## How it works
- Every task declares which apps it may need (e.g., `mail`, `editor`, `browser`).
- When a task runs, the agent checks your permission store.
- If the app is not permitted, it asks for your approval.
- You can revoke permissions any time.

## Next steps
- Connect real integrations (email, editors, OS automation) behind the permission checks.
- Add a UI layer (e.g., a tray app) for approvals.
- Replace stubs with actual API calls or local automation.
