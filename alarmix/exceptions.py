class AlarmDaemonIsNotRunning(Exception):
    ...


class SoundFileNotFound(Exception):
    def __init__(self, sound):
        self.sound = sound

    def __str__(self):
        return f"Sound file '{self.sound}' was not found."
