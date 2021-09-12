from fastapi import Body, APIRouter, HTTPException
from bson import ObjectId, errors
from passlib.context import CryptContext

from database.user import retrieve_users, retrieve_user,update_user_details, delete_user, \
    UserNotFoundException
from models.user import ResponseModel, ErrorResponseModel, UpdateUserModel

router = APIRouter()
hash_helper = CryptContext(schemes=["bcrypt"])


@router.get("/get_all_users")
async def get_users():
    users = retrieve_users()
    return ResponseModel(users, "Users data retrieved successfully") \
        if len(users) > 0 \
        else ResponseModel(
        users, "Empty list returned")


@router.get("/get_user_data/{obj_id}")
def get_user_data(obj_id):
    try:
        user = retrieve_user(_id=ObjectId(obj_id))
        return ResponseModel(user, "User data retrieved successfully")
    except UserNotFoundException as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except errors.InvalidId as ex:
        raise HTTPException(status_code=404, detail=str(ex))

@router.put("/update_user/{obj_id}")
def update_user(obj_id: str, req: UpdateUserModel = Body(...)):
    try:
        update_user_details(obj_id, req.dict())
        return ResponseModel("User with ID: {} name update is successful".format(obj_id),
                             "User name updated successfully")
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="User doesn't exist.")
    except errors.InvalidId as ex:
        raise HTTPException(status_code=404, detail=str(ex))


# @router.delete("/delete_user/{obj_id}")
# def delete_user_data(obj_id: str):
#     delete_user(obj_id)
#     return ResponseModel("User with ID: {} removed".format(obj_id), "User deleted successfully") \
#         if deleted_user \
#         else ErrorResponseModel("An error occurred", 404, "User with obj_id {0} doesn't exist".format(obj_id))
