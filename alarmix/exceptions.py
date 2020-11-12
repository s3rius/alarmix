class AlarmDaemonIsNotRunning(Exception):
    ...


class SoundFileNotFound(Exception):
    def __init__(self, sound_path: str):
        self.sound = sound_path

    def __str__(self) -> str:
        return f"Sound file '{self.sound}' was not found."
