import os.path
import subprocess
import threading
from argparse import Namespace
from datetime import datetime
from time import sleep

from loguru import logger

from alarmix.daemon import lock
from alarmix.daemon.alarm_manager import AlarmManager
from alarmix.exceptions import SoundFileNotFound


class BuzzerThread(threading.Thread):
    def __init__(self, manager: AlarmManager, args: Namespace) -> None:
        threading.Thread.__init__(self)
        self.manager = manager
        self.sound = args.sound
        if not os.path.exists(self.sound):
            raise SoundFileNotFound(self.sound)

    def run(self) -> None:
        logger.debug("Started buzzer thread.")
        while True:
            lock.acquire()
            alarms = self.manager.list_alarms()
            self.manager.cleanup()
            lock.release()
            if len(alarms) > 0:
                now = datetime.now().time().replace(second=0, microsecond=0)
                if alarms[0].time == now:
                    lock.acquire()
                    if self.manager.alarm_pid is None:
                        self.manager.alarm_pid = self.start_alarm()
                    lock.release()
            sleep(20)

    def start_alarm(self) -> int:
        process = subprocess.Popen(["mpv", "--loop", "--no-video", self.sound])
        return process.pid

    def finalize(self) -> None:
        lock.acquire()
        self.manager.cleanup()
        self.manager.dump_alarms()
        lock.release()
