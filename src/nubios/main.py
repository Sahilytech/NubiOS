from __future__ import annotations

import os

from dotenv import load_dotenv

from .ai.provider import LocalAIProvider, MockAIProvider
from .ai.tts import ElevenLabsTTS, NoOpTTS
from .ai.voice_controller import VoiceController
from .config.settings import Settings
from .core.assistant import Assistant
from .core.logger import configure_logging
from .ui.main_window import MainWindow


def main() -> int:
    # Load local configuration before Settings.from_env(). The .env file is
    # intentionally ignored by Git and may contain provider credentials.
    load_dotenv()
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

    tts = NoOpTTS()
    if settings.tts_enabled and settings.tts_provider.casefold() == "elevenlabs" and settings.elevenlabs_api_key:
        tts = ElevenLabsTTS(
            api_key=settings.elevenlabs_api_key,
            voice_id=settings.elevenlabs_voice_id,
            model_id=settings.elevenlabs_model,
            data_dir=settings.data_dir,
        )

    voice = VoiceController()

    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("NubiOS")
    assistant = Assistant(settings, provider, tts=tts)
    window = MainWindow(assistant, voice=voice)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
