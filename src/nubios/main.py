from __future__ import annotations

import os

from .ai.provider import LocalAIProvider, MockAIProvider
from .config.settings import Settings
from .core.assistant import Assistant
from .core.logger import configure_logging
from .ui.main_window import MainWindow


def main() -> int:
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    settings = Settings.from_env()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    configure_logging(settings.data_dir / "logs")

    if settings.mock_ai or settings.ai_provider == "mock":
        provider = MockAIProvider()
    elif settings.ai_provider == "ollama":
        provider = LocalAIProvider(settings.ai_model)
    else:
        provider = MockAIProvider()

    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("NubiOS")
    assistant = Assistant(settings, provider)
    window = MainWindow(assistant)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
