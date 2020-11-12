import os.path
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Iterable, List

from loguru import logger

SOCKET_NAME = "/tmp/timer_socket.sock"


@dataclass
class DeltaAlarm:
    time: time
    delta: timedelta


def calculate_auto_time(event_time: time):
    now = datetime.now()
    new_delta = now.replace(hour=event_time.hour, minute=event_time.minute) - now
    target = now + timedelta(seconds=new_delta.seconds)
    target = target.replace(second=0, microsecond=0)
    return target


def add_delta_to_alarms(alarms_list: Iterable[time]) -> List[DeltaAlarm]:
    now = datetime.now()
    alarms_with_delta = []
    for alarm in alarms_list:
        alarm_time = calculate_auto_time(alarm)
        delta = alarm_time - now
        alarms_with_delta.append(DeltaAlarm(time=alarm, delta=delta))
    return alarms_with_delta


def remove_if_exists(filename: str):
    """
    Removes file
    """
    if os.path.exists(filename):
        logger.debug(f"removing {filename}")
        os.remove(filename)
