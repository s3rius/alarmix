import os.path
from datetime import date, datetime, time, timedelta
from typing import Iterable, List, Optional

from loguru import logger

from alarmix.schema import Alarm, DeltaAlarm, When

SOCKET_NAME = "/tmp/timer_socket.sock"


def calculate_day_offset(to_when: When) -> int:
    today = date.today().weekday()
    offset = 0
    if to_when == When.weekdays and today >= 5:
        offset = 7 - today
    if to_when == When.weekends and today < 5:
        offset = 5 - today
    return offset


def calculate_auto_time(event_time: time, day_offset: Optional[int] = None) -> datetime:
    now = datetime.now()
    new_delta = now.replace(hour=event_time.hour, minute=event_time.minute) - now
    target = now + timedelta(seconds=new_delta.seconds)
    if day_offset:
        target += timedelta(days=day_offset)
    target = target.replace(second=0, microsecond=0)
    return target


def add_delta_to_alarms(alarms_list: Iterable[Alarm]) -> List[DeltaAlarm]:
    now = datetime.now()
    alarms_with_delta = []
    for alarm in alarms_list:
        offset = calculate_day_offset(alarm.when)
        alarm_time = calculate_auto_time(alarm.time, offset)
        delta = alarm_time - now
        alarms_with_delta.append(
            DeltaAlarm(time=alarm.time, when=alarm.when, delta=delta)
        )
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
