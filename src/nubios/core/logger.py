from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "event": record.getMessage(),
            "component": record.name,
            "status": getattr(record, "status", "info"),
        }
        metadata = getattr(record, "metadata", {})
        if isinstance(metadata, dict):
            payload["metadata"] = metadata
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging(log_dir: Path) -> logging.Logger:
    """Configure one rotating-safe JSONL file without logging secrets."""
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("nubios")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not logger.handlers:
        handler = logging.FileHandler(log_dir / "nubios.jsonl", encoding="utf-8")
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    return logger


def audit(logger: logging.Logger, event: str, *, status: str = "ok", **metadata: Any) -> None:
    """Write structured metadata; callers must exclude secrets and private content."""
    safe = {k: v for k, v in metadata.items() if k.lower() not in {"password", "token", "api_key", "secret"}}
    logger.info(event, extra={"status": status, "metadata": safe})
