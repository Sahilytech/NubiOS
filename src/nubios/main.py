from __future__ import annotations

import logging
import os
from .config.settings import Settings
from .core.assistant import Assistant
from .ai.provider import MockAIProvider
from .ui.main_window import MainWindow


def main() -> int:
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    settings = Settings.from_env()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO), format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    assistant = Assistant(settings, MockAIProvider())
    window = MainWindow(assistant)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
