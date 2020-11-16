import enum
from datetime import date, time, timedelta
from typing import List, Optional

from pydantic import BaseModel, Field


class When(str, enum.Enum):
    auto = "auto"
    everyday = "everyday"
    weekdays = "weekdays"
    weekends = "weekends"

    def __str__(self) -> str:
        return str(self.value)


class RequestAction(str, enum.Enum):
    add = "add"
    list = "list"
    stop = "stop"
    delete = "delete"
    cancel = "cancel"


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
    canceled: bool


class InfoList(BaseModel):
    alarms: List[AlarmInfo]


class CanceledAlarm(BaseModel):
    time: time
    canceled: date = Field(default_factory=date.today)

    def __hash__(self) -> int:
        return self.time.__hash__() + self.canceled.__hash__()
