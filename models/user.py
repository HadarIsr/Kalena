from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field


class UserModel(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)
    first_name: str = Field(...)
    last_name: str = Field(...)
    degree: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "email": "israel@mta.ac.il",
                "password": "12345678",
                "first_name": "Israel",
                "last_name": "Israeli",
                "degree": "Computer Science",
            }
        }


class UpdateUserModel(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    city: Optional[str]
    address: Optional[str]
    degree: Optional[str]


    class Config:
        schema_extra = {
            "example": {
                "first_name": "Israel",
                "last_name": "Israeli",
                "city": "Jaffo",
                "address": "Rabeno Yeruham",
                "degree": "Computer Science",
            }
        }


class FindMeeting(BaseModel):
    duration_session: float = Field(...)
    email: List[str] = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "duration_session": 2.0,
                "email": ["Israel@mta.com", "noam@mta.com"]
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
