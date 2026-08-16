from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Intent:
    name: str
    value: str = ""


class IntentEngine:
    def parse(self, text: str) -> Intent:
        t = text.strip()
        low = t.lower()
        if re.match(r"^open\s+", low):
            return Intent("open_application", t.split(None, 1)[1])
        if low.startswith("find "):
            return Intent("find_file", t[5:].strip())
        if low in {"show my tasks", "show tasks", "what are my tasks"}:
            return Intent("show_tasks")
        if low.startswith("add task:"):
            return Intent("add_task", t.split(":", 1)[1].strip())
        if low.startswith("remember that "):
            return Intent("remember", t[len("remember that "):].strip())
        if low.startswith("what do you remember about "):
            return Intent("recall", t[len("what do you remember about "):].strip())
        return Intent("chat", t)
