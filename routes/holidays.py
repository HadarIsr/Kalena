from fastapi import APIRouter
from passlib.context import CryptContext
from database.holidays import retrieve_holidays
from models.event import ResponseModel

router = APIRouter()
hash_helper = CryptContext(schemes=["bcrypt"])


@router.get("/get_holidays")
def get_holidays():
    holidays = retrieve_holidays()
    if len(holidays) > 0:
        return ResponseModel(holidays, "holidays data retrieved successfully") 
    else:
        return ResponseModel(holidays, "No holidays")