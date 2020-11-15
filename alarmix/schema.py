import enum
from datetime import time, timedelta
from typing import List, Optional

from pydantic import BaseModel


class When(str, enum.Enum):
    auto = "auto"
    everyday = "everyday"
    weekdays = "weekdays"
    weekends = "weekends"

    def __str__(self) -> str:
        return str(self.value)


class RequestAction(str, enum.Enum):
    add = "add"
    delete = "delete"
    list = "list"
    stop = "stop"


class TimeMessageBase(BaseModel):
    when: When
    action: RequestAction
    full_list: bool = False


class TimeMessageClient(TimeMessageBase):
    time: Optional[str]


class TimeMessageSocket(TimeMessageBase):
    time: Optional[time]


class Alarm(BaseModel):
    time: time
    when: When

    def __hash__(self) -> int:
        return self.time.__hash__() + self.when.__hash__()


class DeltaAlarm(Alarm):
    delta: timedelta


class AlarmInfo(BaseModel):
    time: time
    remaining: str
    when: str  # Possible values are `When` or date if When == auto


class InfoList(BaseModel):
    alarms: List[AlarmInfo]
