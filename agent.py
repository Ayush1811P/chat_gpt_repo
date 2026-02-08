#!/usr/bin/env python3
"""Agent Aayu: local permissioned assistant skeleton.

This module implements a minimal task runner that requires user permission
before opening apps or websites. It includes a simple chat loop that can
open apps, open websites, and create files on request.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import shlex
import subprocess
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

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

    def _load_permissions(self) -> Dict[str, Dict[str, bool]]:
        if not self.permissions_path.exists():
            return {"apps": {}, "sites": {}}
        with self.permissions_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, dict) and "apps" in data and "sites" in data:
            return data
        # Backward-compatibility for older flat maps
        if isinstance(data, dict):
            return {"apps": data, "sites": {}}
        return {"apps": {}, "sites": {}}

    def _save_permissions(self) -> None:
        with self.permissions_path.open("w", encoding="utf-8") as handle:
            json.dump(self.permissions, handle, indent=2, sort_keys=True)

    def is_allowed(self, category: str, name: str) -> bool:
        return self.permissions.get(category, {}).get(name, False)

    def grant(self, category: str, name: str) -> None:
        self.permissions.setdefault(category, {})[name] = True
        self._save_permissions()

    def revoke(self, category: str, name: str) -> None:
        if name == "all":
            self.permissions[category] = {}
        else:
            self.permissions.get(category, {}).pop(name, None)
        self._save_permissions()

    def ensure_permission(self, category: str, name: str, prompt: str) -> bool:
        if self.is_allowed(category, name):
            return True

        response = input(f"{prompt} (y/N): ").strip().lower()
        if response == "y":
            self.grant(category, name)
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


def speak(message: str) -> None:
    print(f"Aayu: {message}")
    if importlib.util.find_spec("pyttsx3") is None:
        return
    pyttsx3 = importlib.import_module("pyttsx3")
    engine = pyttsx3.init()
    engine.say(message)
    engine.runAndWait()


def run_task(permission_manager: PermissionManager, task: TaskRequest) -> None:
    for app in task.required_apps:
        if not permission_manager.ensure_permission(
            "apps",
            app,
            f"Permission required to open '{app}'. Allow?",
        ):
            speak(f"Denied. '{task.name}' requires '{app}'.")
            return
    task.handler(permission_manager)


class AppController:
    def __init__(self, permission_manager: PermissionManager) -> None:
        self.permission_manager = permission_manager

    def open_app(self, app_name: str, display_name: str, commands: List[str]) -> None:
        if not self.permission_manager.ensure_permission(
            "apps",
            app_name,
            f"Allow Aayu to open {display_name}?",
        ):
            speak(f"Okay, I won't open {display_name}.")
            return
        self._run_command(commands, display_name)

    def open_chrome(self) -> None:
        system = platform.system().lower()
        if system == "darwin":
            commands = ["open", "-a", "Google Chrome"]
        elif system == "windows":
            commands = ["cmd", "/c", "start", "", "chrome"]
        else:
            commands = ["google-chrome"]
        self.open_app("chrome", "Google Chrome", commands)

    def open_vs_code(self) -> None:
        system = platform.system().lower()
        if system == "darwin":
            commands = ["open", "-a", "Visual Studio Code"]
        elif system == "windows":
            commands = ["cmd", "/c", "start", "", "code"]
        else:
            commands = ["code"]
        self.open_app("vscode", "VS Code", commands)

    def open_website(self, url: str) -> None:
        domain = url.split("//")[-1].split("/")[0]
        if not self.permission_manager.ensure_permission(
            "sites",
            domain,
            f"Allow Aayu to open {domain}?",
        ):
            speak(f"Okay, I won't open {domain}.")
            return
        webbrowser.open(url)
        speak(f"Opening {url}.")

    @staticmethod
    def _run_command(commands: List[str], display_name: str) -> None:
        try:
            subprocess.Popen(commands)
            speak(f"Opening {display_name} now.")
        except FileNotFoundError:
            speak(
                f"I couldn't find {display_name}. Make sure it is installed and in PATH."
            )


# --- Example task handlers ---

def draft_email(_: PermissionManager) -> None:
    speak("[stub] Drafting an email... (connect to your email client here)")


def open_editor(_: PermissionManager) -> None:
    speak("[stub] Opening your code editor... (connect to automation here)")


def send_message(_: PermissionManager) -> None:
    speak("[stub] Sending a message... (connect to messaging client here)")


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


def create_python_calculator(target_path: Path) -> None:
    calculator_code = (
        "def add(a, b):\n"
        "    return a + b\n\n"
        "def subtract(a, b):\n"
        "    return a - b\n\n"
        "def multiply(a, b):\n"
        "    return a * b\n\n"
        "def divide(a, b):\n"
        "    if b == 0:\n"
        "        raise ValueError('Cannot divide by zero')\n"
        "    return a / b\n\n"
        "def main():\n"
        "    operations = {\n"
        "        '+': add,\n"
        "        '-': subtract,\n"
        "        '*': multiply,\n"
        "        '/': divide,\n"
        "    }\n"
        "    symbol = input('Choose operation (+, -, *, /): ').strip()\n"
        "    if symbol not in operations:\n"
        "        print('Invalid operation')\n"
        "        return\n"
        "    a = float(input('First number: '))\n"
        "    b = float(input('Second number: '))\n"
        "    result = operations[symbol](a, b)\n"
        "    print(f'Result: {result}')\n\n"
        "if __name__ == '__main__':\n"
        "    main()\n"
    )
    target_path.write_text(calculator_code, encoding="utf-8")
    speak(f"Created {target_path} with a calculator program.")


def parse_request(text: str) -> Tuple[str, Optional[str]]:
    lowered = text.lower().strip()
    if "open chrome" in lowered:
        return "open_chrome", None
    if "open vs code" in lowered or "open vscode" in lowered:
        return "open_vscode", None
    if "open" in lowered and "http" in lowered:
        tokens = shlex.split(text)
        for token in tokens:
            if token.startswith("http://") or token.startswith("https://"):
                return "open_website", token
    if "create" in lowered and lowered.endswith(".py") and "calculator" in lowered:
        filename = lowered.split("create", 1)[1].split("and", 1)[0].strip()
        return "create_calculator", filename
    return "unknown", None


def handle_chat(permission_manager: PermissionManager) -> None:
    controller = AppController(permission_manager)
    speak("Hi, I'm Agent Aayu. Tell me what you want me to do.")
    while True:
        user_text = input("You: ").strip()
        if not user_text:
            continue
        if user_text.lower() in {"quit", "exit"}:
            speak("Goodbye!")
            break
        action, value = parse_request(user_text)
        if action == "open_chrome":
            controller.open_chrome()
            continue
        if action == "open_vscode":
            controller.open_vs_code()
            continue
        if action == "open_website" and value:
            controller.open_website(value)
            continue
        if action == "create_calculator" and value:
            create_python_calculator(Path(value))
            continue
        speak(
            "I can open Chrome, open VS Code, open a website URL, or create a Python calculator file."
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Agent Aayu (permissioned assistant)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-tasks", help="List available tasks")

    run_parser = subparsers.add_parser("run-task", help="Run a task by name")
    run_parser.add_argument("task_name", help="Task name to run")

    grant_parser = subparsers.add_parser("grant", help="Grant app permission")
    grant_parser.add_argument("app_name", help="App name to grant")

    revoke_parser = subparsers.add_parser("revoke", help="Revoke app permission")
    revoke_parser.add_argument("app_name", help="App name to revoke or 'all'")

    subparsers.add_parser("chat", help="Start an interactive chat session")

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
        permissions.grant("apps", args.app_name)
        speak(f"Granted: {args.app_name}")
        return

    if args.command == "revoke":
        permissions.revoke("apps", args.app_name)
        speak(f"Revoked: {args.app_name}")
        return

    if args.command == "run-task":
        task = registry.get(args.task_name)
        if not task:
            speak(f"Unknown task: {args.task_name}")
            return
        run_task(permissions, task)
        return

    if args.command == "chat":
        handle_chat(permissions)


if __name__ == "__main__":
    main()
