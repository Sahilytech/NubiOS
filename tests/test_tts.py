from __future__ import annotations

import json

from nubios.ai.tts import ElevenLabsTTS, NoOpTTS


def test_nubi_voice_id_is_default() -> None:
    provider = ElevenLabsTTS(api_key="test-key")
    assert provider.voice_id == "fJ2BRu9MMKDzgQZh6OiH"
    assert provider.model_id == "eleven_multilingual_v2"


def test_noop_tts_is_safe() -> None:
    assert NoOpTTS().speak("Hello Nubi") is None


def test_synthesize_builds_expected_request(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b"audio"

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["headers"] = dict(request.headers)
        captured["body"] = json.loads(request.data.decode("utf-8"))
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    provider = ElevenLabsTTS(api_key="test-key")
    assert provider.synthesize("Hola, soy Nubi") == b"audio"
    assert captured["url"] == (
        "https://api.elevenlabs.io/v1/text-to-speech/"
        "fJ2BRu9MMKDzgQZh6OiH?output_format=mp3_44100_128"
    )
    assert captured["body"]["text"] == "Hola, soy Nubi"
    assert captured["body"]["model_id"] == "eleven_multilingual_v2"
    assert captured["timeout"] == 60
