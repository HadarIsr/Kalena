from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from database.event import retrieve_mutual_events, EventNotFoundException
from database.friend import get_friends_list, retrieve_friends_request, retrieve_friend, delete_friend, \
    send_friend_request, decline_friend_request, accept_friend_request, FriendNotFoundException
from database.user import UserNotFoundException
from models.user import ResponseModel
from bson import errors

router = APIRouter()
hash_helper = CryptContext(schemes=["bcrypt"])

@router.get("/get_friends_list/{user_id}")
def get_user_friends(user_id: str):
    try:
        friends = get_friends_list(user_id)
        return ResponseModel(friends, "friend data retrieved successfully")
    except FriendNotFoundException:
        raise HTTPException(status_code=404, detail="Friend doesn't exist.")
    except errors.InvalidId as ex:
         raise HTTPException(status_code=404, detail=str(ex))

@router.get("/get_friend_data/{friend_id}")
def get_user_friend(friend_id: str):
    try:
        friend = retrieve_friend(friend_id)
        return ResponseModel(friend, "friend data retrieved successfully")
    except FriendNotFoundException:
        raise HTTPException(status_code=404, detail="Friend doesn't exist.")
    except errors.InvalidId as ex:
         raise HTTPException(status_code=404, detail=str(ex))

@router.get("/get_friend_requests/{user_id}")
def get_user_friend(user_id: str):
    try:
        friends = retrieve_friends_request(user_id)
        return ResponseModel(friends, "friend data retrieved successfully")
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="User doesn't exist.")
    except errors.InvalidId as ex:
         raise HTTPException(status_code=404, detail=str(ex))

@router.get("/get_mutual_events/{user_id}/{friend_id}")
def get_mutual_events(user_id: str, friend_id: str):
    try:
        events = retrieve_mutual_events(user_id, friend_id)
        return ResponseModel(events, "Events data retrieved successfully")
    except EventNotFoundException:
        raise HTTPException(status_code=404, detail="Event doesn't exist.")
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="User doesn't exist.")
    except errors.InvalidId as ex:
         raise HTTPException(status_code=404, detail=str(ex))

@router.patch("/send_friend_req/{user_id}/{friend_email}")
def put_friend_request(user_id: str, friend_email: str):
    try:
        send_friend_request(user_id, friend_email)
        return ResponseModel("req", "sent successfully")
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="User doesn't exist.")
    except FriendNotFoundException as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    except errors.InvalidId as ex:
         raise HTTPException(status_code=404, detail=str(ex))

@router.patch("/approved_friend_req/{user_id}/{friend_id}")
def approved_friend_req(user_id: str, friend_id: str):
    try:
        accept_friend_request(user_id, friend_id)
        return ResponseModel("friend_id", "request approved updated in database" )
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="User doesn't exist.")
    except FriendNotFoundException as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except errors.InvalidId as ex:
         raise HTTPException(status_code=404, detail=str(ex))

@router.patch("/decline_friend_req/{user_id}/{friend_id}")
def decline_friend_req(user_id: str, friend_id: str):
    try:
        decline_friend_request(user_id, friend_id)
        return ResponseModel("friend_id", "request approved updated in database" )
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="User doesn't exist.")
    except FriendNotFoundException as ex:
        raise HTTPException(status_code=404, detail=str(ex))


@router.delete("/delete_friend/{user_id}/{friend_id}")
def delete_user_friend(user_id: str, friend_id: str):
    try:
        delete_friend(user_id, friend_id)
        return ResponseModel("friend with ID: {} removed".format(friend_id), "deleted successfully")
    except FriendNotFoundException as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except UserNotFoundException as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except errors.InvalidId as ex:
         raise HTTPException(status_code=404, detail=str(ex))