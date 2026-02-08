# Agent Aayu (Local Permissioned AI Assistant)

This repo provides a minimal, local-first AI agent skeleton that **requires explicit user permission** before it can open apps or websites. It is designed for privacy: you can grant one-time or persistent access per app or site, and revoke access at any time.

## Features
- Explicit permission prompts before the agent opens an app or website.
- Local permissions store (`permissions.json`) you control.
- Interactive chat loop (Agent Aayu) for simple commands.
- Extensible task registry (add new tasks safely).

## Quick start
```bash
python agent.py chat
```

Example commands you can say:
- `open chrome`
- `open vs code`
- `open https://example.com`
- `create calculator.py and write a calculator using python`

## Other CLI commands
```bash
python agent.py list-tasks
python agent.py run-task "draft_email"
python agent.py grant "chrome"
python agent.py revoke "chrome"
```

## How it works
- Every app or site requires your approval the first time it is opened.
- The agent stores your permissions locally and reuses them until revoked.
- You can revoke permissions any time.

## Next steps
- Connect real integrations (email, editors, OS automation) behind the permission checks.
- Add a UI layer (e.g., a tray app) for approvals.
- Replace stubs with actual API calls or local automation.
