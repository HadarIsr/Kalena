from fastapi import Body, APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from passlib.context import CryptContext
from database.event import decline_invite, accept_invite, retrieve_user_invitees_event, \
    retrieve_user_event, update_event_details, add_event_to_users, remove_user_event,\
    EventNotFoundException, retrieve_user_events
from database.user import UserNotFoundException
from models.event import EventModel, UpdateEventModel, ResponseModel
from bson import errors

router = APIRouter()
hash_helper = CryptContext(schemes=["bcrypt"])


@router.post("/post_event/{user_id}")
def post_user_event(user_id: str, event: EventModel = Body(...)):
    try:
        event = jsonable_encoder(event)
        events = add_event_to_users(user_id, event)
        return ResponseModel(events, "User event added successfully.")

    except UserNotFoundException or errors.InvalidId as ex:
        raise HTTPException(status_code=404, detail=str(ex))


@router.patch("/update_event/{user_id}/{event_id}")
def update_user_event(user_id: str, event_id: str, event: UpdateEventModel = Body(...)):
    try:
        update_event = update_event_details(user_id, event_id, event.dict())
        return ResponseModel(update_event, "User event updated successfully.")
    except EventNotFoundException or errors.InvalidId as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="User doesn't exist.")


@router.get("/get_user_events/{user_id}")
def get_user_events(user_id: str):
    try:
        events = retrieve_user_events(user_id)
        if len(events) > 0:
            return ResponseModel(events, "Events data retrieved successfully")
        else:
            return ResponseModel(events, "No events")
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="No events")
    except errors.InvalidId as ex:
        raise HTTPException(status_code=404, detail=str(ex))


@router.get("/get_user_event/{user_id}/{event_id}")
def get_event(user_id: str, event_id: str):
    try:
        event = retrieve_user_event(user_id, event_id)
        return ResponseModel(event, "Events data retrieved successfully") 
    except EventNotFoundException:
        raise HTTPException(status_code=404, detail="User doesn't exist.")
    except errors.InvalidId as ex:
        raise HTTPException(status_code=404, detail=str(ex))


@router.get("/get_event_invitations/{user_id}")
def get_event_invitations(user_id: str):
    try:
        events = retrieve_user_invitees_event(user_id)
        if events:
            return ResponseModel(events, "Event invitations retrieved successfully")
        else:
            return ResponseModel([], "No event invitations found")
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="User doesn't exist.")
    except errors.InvalidId as ex:
        raise HTTPException(status_code=404, detail=str(ex))


@router.put("/response_to_invitation/{user_id}/{event_id}/{response}")
def response_to_invitation(user_id: str, event_id: str, response: str):
    try:
        if response == "Yes":
            accept_invite(user_id, event_id)
            return ResponseModel("success", f"user: {user_id} accept {event_id}")
        elif response == "No":
            decline_invite(user_id, event_id)
            return ResponseModel("success", f"user: {user_id} decline {event_id}")
        else:
            raise HTTPException(status_code=404, detail=f"{response} unsupported")

    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="User doesn't exist.")
    except EventNotFoundException:
        raise HTTPException(status_code=404, detail="Event doesn't exist.")
    except errors.InvalidId as ex:
        raise HTTPException(status_code=404, detail=str(ex))


@router.delete("/delete_event/{user_id}/{event_id}")
def delete_user_event(user_id: str, event_id: str):
    try:
        remove_user_event(user_id, event_id)
        return ResponseModel('delete', "User event successfully removed.")
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="User doesn't exist.")
    except EventNotFoundException:
        raise HTTPException(status_code=404, detail="Event doesn't exist.")
    except errors.InvalidId as ex:
        raise HTTPException(status_code=404, detail=str(ex))

