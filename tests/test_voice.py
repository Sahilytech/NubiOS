from nubios.ai.voice_controller import VoiceController


def test_voice_controller_rejects_non_positive_duration() -> None:
    voice = VoiceController()
    try:
        voice.listen_once(0)
    except ValueError as exc:
        assert "positive" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_microphone_availability_is_boolean() -> None:
    assert isinstance(VoiceController.microphone_available(), bool)
