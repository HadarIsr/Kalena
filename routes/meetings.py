from database.find_a_meeting import meet_us
from database.user import UserNotFoundException
from fastapi import APIRouter, Body, HTTPException
from passlib.context import CryptContext
from fastapi.encoders import jsonable_encoder
from models.event import ResponseModel
from models.user import FindMeeting
from bson import errors

router = APIRouter()
hash_helper = CryptContext(schemes=["bcrypt"])


@router.post("/find_meeting")
def find_a_meeting(data: FindMeeting = Body(...)):
    try:
        data = jsonable_encoder(data)
        duration_session = data['duration_session']
        guests_email = data['email']
        meeting = meet_us(guests_email, duration_session)
        return ResponseModel(meeting, "User event added successfully.")

    except UserNotFoundException as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except errors.InvalidId as ex:
         raise HTTPException(status_code=404, detail=str(ex))
