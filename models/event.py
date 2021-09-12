from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class EventModel(BaseModel):
    creator: str = Field(...)
    title: str = Field(...)
    start_date: datetime = Field(...)
    end_date: datetime = Field(...)
    invitees: List[str] = Field(default=None)
    participants: List[str] = Field(default=None)
    description: str = Field(default=None)
    location: str = Field(default=None)
    repeat: str = Field(default=None)
    color: str = Field(...)
    all_day: bool = Field(default=False)

    class Config:
        schema_extra = {
            "example": {
                "creator": "israel@mta.ac.il",
                "title": "Beer with friends",
                "start_date": '2021-11-10T11:15:00+00:00',
                "end_date": '2021-11-10T12:15:00+00:00',
                "invitees": [],
                "participants": [],
                "description": "Happy gathering with friends",
                "location": "TBD",
                "repeat": "None",
                "color": "yellow",
                "all_day": "False"
            }
        }


class UpdateEventModel(BaseModel):
    title: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    description: Optional[str]
    location: Optional[str]
    color: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "title": "Beer with friends",
                "start_date": '2021-08-28T20:00:00+00:00',
                "end_date": '2021-08-28T21:00:00+00:00',
                "description": "Happy gathering with friends",
                "location": "Bar x",
                "color": "yellow",
            }
        }


class AddCourses(BaseModel):
    courses_list: List[str] = Field(default=None)

    class Config:
        schema_extra = {
            "example": {
                   "courses_list": ["6128edebd4d4a6f14b3c63a2", "6128edebd4d4a6f14b3c63b0"],
            }
        }

def ResponseModel(data, message):
    return {
        "data": data,
        "code": 200,
        "message": message,
    }

def ErrorResponseModel(error, code, message):
    return {
        "error": error,
        "code": code,
        "message": message
    }
