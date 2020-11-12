import os.path
import pickle
import signal
from collections import defaultdict
from datetime import date, datetime, time
from operator import attrgetter
from typing import DefaultDict, List, Optional, Set, Union

from loguru import logger
from prettytable import PrettyTable

from alarmix.schema import RequestAction, TimeMessageSocket, When
from alarmix.utils import DeltaAlarm, add_delta_to_alarms, calculate_auto_time


class AlarmManager:
    """
    AlarmManager manipulates your alarms
    """

    def __init__(self, dump_file: str):
        self.dump_file = dump_file
        self.alarm_pid: Optional[int] = None
        self.alarms: DefaultDict[Set[Union[time, datetime]]] = defaultdict(set)

    def process_message(self, msg: TimeMessageSocket) -> str:
        """
        Update alarms by TimeMessageSocket action.
        Delete|Add|List|Stop.
        """
        if msg.action == RequestAction.delete:
            self.del_alarm(msg.time, msg.when)
            return "Successfully deleted"
        elif msg.action == RequestAction.add:
            self.add_alarm(msg.time, msg.when)
            return "Successfully added"
        elif msg.action == RequestAction.list:
            return self.list_formatted()
        elif msg.action == RequestAction.stop:
            return self.stop_alarm()

        self.dump_alarms()

    def list_formatted(self) -> str:
        """
        Will return string containing table. Such as:
            +------------+----------------+
            | alarm time | remaining time |
            +------------+----------------+
            |    10:0    |    11:36:06    |
            +------------+----------------+
        """
        table = PrettyTable(field_names=["alarm time", "remaining time"])
        alarms = self.list_alarms()
        for alarm in alarms:
            table.add_row(
                [
                    f"{alarm.time.hour}:{alarm.time.minute}",
                    str(alarm.delta).split(".")[0],
                ]
            )
        return table.get_string()

    def add_alarm(self, event_time: time, when: When):
        logger.debug(f"Adding {event_time}")
        target = event_time
        if when == When.auto:
            target = calculate_auto_time(event_time)
        self.alarms[when.value].add(target)

    def del_alarm(self, event_time: time, when: When):
        """
        Delete alarm from queue
        """
        logger.debug(f"Trying delete {event_time}")
        target = event_time
        if when == When.auto:
            target = calculate_auto_time(event_time)
        self.alarms[when.value].discard(target)

    def list_alarms(self) -> List[DeltaAlarm]:
        """
        List alarms sorted by time
        """
        needed_keys = [When.everyday.value]
        if date.today().weekday() < 5:
            needed_keys.append(When.weekdays.value)
        else:
            needed_keys.append(When.weekends.value)
        alarms = set()
        for key in needed_keys:
            alarms.update(self.alarms[key])

        for alarm in self.alarms[When.auto.value]:
            if date.today() == alarm.date():
                alarms.add(alarm.time())
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

    def cleanup(self):
        """
        Remove all outdated auto calculated alarms.
        """
        correct_alarms = set()
        for alarm_time in self.alarms[When.auto.value]:
            if alarm_time >= datetime.now():
                correct_alarms.add(alarm_time)
        self.alarms[When.auto.value] = correct_alarms

    def dump_alarms(self):
        with open(self.dump_file, "wb") as file:
            pickle.dump(self.alarms, file)

    def load_alarms(self):
        if not os.path.exists(self.dump_file):
            return []
        with open(self.dump_file, "rb") as file:
            self.alarms = pickle.load(file)
