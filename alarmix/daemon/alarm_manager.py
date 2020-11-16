import os.path
import pickle
import signal
from collections import defaultdict
from datetime import date, datetime, time
from operator import attrgetter
from typing import DefaultDict, List, Optional, Set, Union

from loguru import logger

from alarmix.schema import (
    Alarm,
    AlarmInfo,
    CanceledAlarm,
    DeltaAlarm,
    InfoList,
    RequestAction,
    TimeMessageSocket,
    When,
)
from alarmix.utils import add_delta_to_alarms, calculate_auto_time


class AlarmManager:
    """
    AlarmManager manipulates your alarms
    """

    def __init__(self, dump_file: str):
        self.dump_file = dump_file
        self.alarm_pid: Optional[int] = None
        self.alarms: DefaultDict[str, Set[Union[time, datetime]]] = defaultdict(set)
        self.canceled: DefaultDict[str, Set[CanceledAlarm]] = defaultdict(set)

    def process_message(self, msg: TimeMessageSocket) -> str:
        """
        Update alarms by TimeMessageSocket action.
        Delete|Add|List|Stop.
        """
        message = "Something happened"
        if msg.action == RequestAction.delete:
            self.del_alarm(msg.time, msg.when)
            self.dump_alarms()
            message = "Successfully deleted"
        elif msg.action == RequestAction.add:
            self.add_alarm(msg.time, msg.when)
            self.dump_alarms()
            message = "Successfully added"
        elif msg.action == RequestAction.cancel:
            self.cancel_alarm(msg.time)
            self.dump_alarms()
            message = "Alarm cancelled"
        elif msg.action == RequestAction.list:
            message = self.list_formatted(msg.full_list).json()
        elif msg.action == RequestAction.stop:
            message = self.stop_alarm()
        return message

    def list_formatted(self, all_alarms: bool = False) -> InfoList:
        """
        Returns information about alarms
        """
        alarms = self.list_alarms(all_alarms)
        info_list = list()
        for alarm in alarms:
            when_str = alarm.when.value
            if alarm.when == When.auto:
                date_time = calculate_auto_time(
                    alarm.time,
                )
                when_str = str(date_time.date())
            info_list.append(
                AlarmInfo(
                    time=alarm.time,
                    remaining=str(alarm.delta).split(".")[0],
                    when=when_str,
                    canceled=self.is_canceled(alarm.time, when=alarm.when),
                )
            )
        return InfoList(alarms=info_list)

    def add_alarm(self, event_time: time, when: When) -> None:
        logger.debug(f"Adding {event_time}")
        target = event_time
        if when == When.auto:
            target = calculate_auto_time(event_time)
        self.alarms[when.value].add(target)

    def del_alarm(self, event_time: time, when: When) -> None:
        """
        Delete alarm from queue
        """
        logger.debug(f"Trying delete {event_time}")
        target = event_time
        if when == When.auto:
            target = calculate_auto_time(event_time)
        self.alarms[when.value].discard(target)

    def cancel_alarm(self, event_time: time) -> None:
        """
        Cancel alarm for today
        """
        alarms = self.list_alarms()
        for alarm in alarms:
            if alarm.time == event_time:
                if alarm.when == When.auto:
                    self.del_alarm(event_time, When.auto)
                else:
                    self.canceled[alarm.when.value].add(CanceledAlarm(time=event_time))

    def is_canceled(self, event_time: time, when: When) -> bool:
        today = date.today()
        for alarm in self.canceled[when.value]:
            if alarm.time == event_time and alarm.canceled == today:
                return True
        return False

    def list_alarms(self, all_alarms: bool = False) -> List[DeltaAlarm]:
        """
        List alarms sorted by time
        """
        needed_keys = [When.everyday.value]
        if date.today().weekday() < 5 or all_alarms:
            needed_keys.append(When.weekdays.value)
        if date.today().weekday() >= 5 or all_alarms:
            needed_keys.append(When.weekends.value)
        alarms = set()
        for key in needed_keys:
            for alarm in self.alarms[key]:
                alarms.add(Alarm(time=alarm, when=key))

        for alarm in self.alarms[When.auto.value]:
            if date.today() == alarm.date() or all_alarms:  # type: ignore
                alarms.add(Alarm(time=alarm.time(), when=When.auto))  # type: ignore
        delta_alarms = add_delta_to_alarms(alarms)
        return list(sorted(delta_alarms, key=attrgetter("delta")))

    def stop_alarm(self) -> str:
        """
        Stop alarm by pid.
        Buzzer thread updates alarm_pid variable.
        """
        if self.alarm_pid:
            os.kill(self.alarm_pid, signal.SIGTERM)
            self.alarm_pid = None
            return "Alarm stopped"
        return "Alarm isn't running"

    def cleanup(self) -> None:
        """
        Remove all outdated auto calculated alarms.
        """
        now = datetime.now()
        auto_alarms = self.alarms[When.auto.value]
        self.alarms[When.auto.value] = {
            alarm for alarm in auto_alarms if alarm >= now  # type: ignore
        }
        today = date.today()
        for key in self.canceled.keys():
            self.canceled[key] = set(
                [alarm for alarm in self.canceled[key] if alarm.canceled >= today]
            )

    def dump_alarms(self) -> None:
        with open(self.dump_file, "wb") as file:
            pickle.dump(self, file)

    def load_alarms(self) -> None:
        if not os.path.exists(self.dump_file):
            return None
        with open(self.dump_file, "rb") as file:
            old_manager: AlarmManager = pickle.load(file)
            self.alarms = old_manager.alarms
            self.canceled = old_manager.canceled
            logger.debug("Alarms loaded")
