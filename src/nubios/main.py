from __future__ import annotations

import logging
import os

from .ai.provider import MockAIProvider, OpenAICompatibleProvider
from .config.settings import Settings
from .core.assistant import Assistant
from .ui.main_window import MainWindow


def build_ai_provider(settings: Settings):
    if settings.mock_ai or settings.ai_provider in {"mock", ""}:
        return MockAIProvider()
    if settings.ai_provider in {"openai", "openai-compatible"}:
        return OpenAICompatibleProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            base_url=settings.openai_base_url,
        )
    raise ValueError(f"Unknown AI provider: {settings.ai_provider}")


def main() -> int:
    # Keep optional voice imports completely outside the UI startup path.
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    settings = Settings.from_env()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    from PySide6.QtWidgets import QApplication, QMessageBox

    app = QApplication.instance() or QApplication([])
    app.setApplicationName("NubiOS")
    app.setOrganizationName("NubiWorks")

    try:
        ai = build_ai_provider(settings)
    except Exception as exc:
        logging.getLogger("nubios.startup").exception("ai_provider_init_failed")
        QMessageBox.warning(None, "NubiOS", f"Real AI is unavailable. Nubi will start in local mode.\n\n{exc}")
        ai = MockAIProvider()

    assistant = Assistant(settings, ai)
    window = MainWindow(assistant)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
