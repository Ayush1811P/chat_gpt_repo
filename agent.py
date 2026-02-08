#!/usr/bin/env python3
"""Local permissioned AI agent skeleton.

This module implements a minimal task runner that requires user permission
before opening apps or performing tasks. It is designed to be extended with
real integrations (email, editor, OS automation) while keeping privacy first.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional

PERMISSIONS_FILE = Path("permissions.json")


@dataclass(frozen=True)
class TaskRequest:
    name: str
    description: str
    required_apps: List[str]
    handler: Callable[["PermissionManager"], None]


class PermissionManager:
    def __init__(self, permissions_path: Path = PERMISSIONS_FILE) -> None:
        self.permissions_path = permissions_path
        self.permissions = self._load_permissions()

    def _load_permissions(self) -> Dict[str, bool]:
        if not self.permissions_path.exists():
            return {}
        with self.permissions_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _save_permissions(self) -> None:
        with self.permissions_path.open("w", encoding="utf-8") as handle:
            json.dump(self.permissions, handle, indent=2, sort_keys=True)

    def is_allowed(self, app_name: str) -> bool:
        return self.permissions.get(app_name, False)

    def grant(self, app_name: str) -> None:
        self.permissions[app_name] = True
        self._save_permissions()

    def revoke(self, app_name: str) -> None:
        if app_name == "all":
            self.permissions = {}
        else:
            self.permissions.pop(app_name, None)
        self._save_permissions()

    def ensure_permission(self, app_name: str) -> bool:
        if self.is_allowed(app_name):
            return True

        response = input(
            f"Permission required to open '{app_name}'. Allow? (y/N): "
        ).strip().lower()
        if response == "y":
            self.grant(app_name)
            return True
        return False


class TaskRegistry:
    def __init__(self) -> None:
        self._tasks: Dict[str, TaskRequest] = {}

    def register(self, task: TaskRequest) -> None:
        self._tasks[task.name] = task

    def list_tasks(self) -> List[TaskRequest]:
        return list(self._tasks.values())

    def get(self, name: str) -> Optional[TaskRequest]:
        return self._tasks.get(name)


registry = TaskRegistry()


def run_task(permission_manager: PermissionManager, task: TaskRequest) -> None:
    for app in task.required_apps:
        if not permission_manager.ensure_permission(app):
            print(f"Denied: '{task.name}' requires '{app}'.")
            return
    task.handler(permission_manager)


# --- Example task handlers ---

def draft_email(_: PermissionManager) -> None:
    print("[stub] Drafting an email... (connect to your email client here)")


def open_editor(_: PermissionManager) -> None:
    print("[stub] Opening your code editor... (connect to automation here)")


def send_message(_: PermissionManager) -> None:
    print("[stub] Sending a message... (connect to messaging client here)")


registry.register(
    TaskRequest(
        name="draft_email",
        description="Draft an email using your local email app.",
        required_apps=["mail"],
        handler=draft_email,
    )
)

registry.register(
    TaskRequest(
        name="open_editor",
        description="Open your code editor to help with coding.",
        required_apps=["editor"],
        handler=open_editor,
    )
)

registry.register(
    TaskRequest(
        name="send_message",
        description="Send a message in your chat app.",
        required_apps=["messaging"],
        handler=send_message,
    )
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local permissioned AI agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-tasks", help="List available tasks")

    run_parser = subparsers.add_parser("run-task", help="Run a task by name")
    run_parser.add_argument("task_name", help="Task name to run")

    grant_parser = subparsers.add_parser("grant", help="Grant app permission")
    grant_parser.add_argument("app_name", help="App name to grant")

    revoke_parser = subparsers.add_parser("revoke", help="Revoke app permission")
    revoke_parser.add_argument("app_name", help="App name to revoke or 'all'")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    permissions = PermissionManager()

    if args.command == "list-tasks":
        for task in registry.list_tasks():
            apps = ", ".join(task.required_apps) or "none"
            print(f"{task.name}: {task.description} (apps: {apps})")
        return

    if args.command == "grant":
        permissions.grant(args.app_name)
        print(f"Granted: {args.app_name}")
        return

    if args.command == "revoke":
        permissions.revoke(args.app_name)
        print(f"Revoked: {args.app_name}")
        return

    if args.command == "run-task":
        task = registry.get(args.task_name)
        if not task:
            print(f"Unknown task: {args.task_name}")
            return
        run_task(permissions, task)


if __name__ == "__main__":
    main()
