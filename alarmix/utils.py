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


def calculate_auto_time(event_time: time) -> datetime:
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


def remove_if_exists(filename: str) -> None:
    """
    Removes file
    """
    if os.path.exists(filename):
        logger.debug(f"removing {filename}")
        os.remove(filename)


def parse_relative_time(relative_time_str: str) -> str:
    if relative_time_str.startswith("+"):
        now = datetime.now().replace(second=0, microsecond=0)
        time_values = relative_time_str.lstrip("+").split(":")
        if len(time_values) == 2:
            hours, minutes = time_values
            new_time = now + timedelta(hours=int(hours), minutes=int(minutes))
        elif len(time_values) == 1:
            new_time = now + timedelta(minutes=int(time_values[0]))
        else:
            return relative_time_str
        return f"{new_time.hour}:{new_time.minute}"
    return relative_time_str
