from app.application.use_cases import AudioStreamer


def get_audio_streamer() -> AudioStreamer:
    return AudioStreamer()
