from __future__ import annotations

from dataclasses import dataclass, field
import re


@dataclass(frozen=True)
class Intent:
    name: str
    value: str = ""
    confidence: float = 1.0
    parameters: dict[str, str] = field(default_factory=dict)


class IntentEngine:
    """Deterministic parser for safe, high-frequency desktop commands."""

    def parse(self, text: str) -> Intent:
        t = text.strip()
        low = t.casefold()
        if not t:
            return Intent("chat", "", 1.0)
        if re.match(r"^(open|launch|start)\s+", low):
            value = re.sub(r"^(open|launch|start)\s+", "", t, flags=re.I).strip().rstrip(".")
            return Intent("open_application", value, 0.98, {"application": value})
        if low.startswith(("find ", "search for ", "look for ")):
            value = re.sub(r"^(find|search for|look for)\s+", "", t, flags=re.I).strip()
            return Intent("find_file", value, 0.96, {"query": value})
        if low in {"show my tasks", "show tasks", "what are my tasks", "what do i have pending", "what do i have pending?"}:
            return Intent("show_tasks", confidence=0.99)
        if low.startswith(("add task:", "add a task:", "add task ")):
            value = re.sub(r"^add (?:a )?task(?::|\s)+", "", t, flags=re.I).strip()
            return Intent("add_task", value, 0.99, {"title": value})
        if low.startswith(("complete task ", "mark ")) and "complete" in low:
            value = re.sub(r"^(complete task|mark)\s+", "", t, flags=re.I).strip()
            value = re.sub(r"\s+as\s+complete\.?$", "", value, flags=re.I)
            return Intent("complete_task", value, 0.95, {"task": value})
        if low.startswith("remember that "):
            value = t[len("remember that "):].strip()
            return Intent("remember", value, 0.99, {"content": value})
        if low.startswith("what do you remember about "):
            value = t[len("what do you remember about "):].strip()
            return Intent("recall", value, 0.99, {"query": value})
        return Intent("chat", t, 0.50, {"text": t})
