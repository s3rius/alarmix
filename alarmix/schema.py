import enum
from datetime import time
from typing import Optional

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
    delete = "delete"
    list = "list"
    stop = "stop"


class TimeMessageBase(BaseModel):
    when: When
    action: RequestAction


class TimeMessageClient(TimeMessageBase):
    time: Optional[str]


class TimeMessageSocket(TimeMessageBase):
    time: Optional[time]


class Alarm(BaseModel):
    hours: int
    minutes: int
    when: When = Field(When.auto)
