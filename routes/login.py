from fastapi import Body, APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBasicCredentials
from passlib.context import CryptContext

from auth.jwt_handler import signJWT
from database.database import admin_collection, add_admin
from database.user import add_user, retrieve_user, user_collection
from models.admin import AdminModel
from models.user import UserModel

router = APIRouter()

hash_helper = CryptContext(schemes=["bcrypt"])


# @router.post("/admin_login")
# def admin_login(admin_credentials: HTTPBasicCredentials = Body(...)):
#     admin_user = admin_collection.find_one({"email": admin_credentials.username}, {"_id": 0})
#     if admin_user:
#         password = hash_helper.verify(
#             admin_credentials.password, admin_user["password"])
#         if password:
#             return signJWT(admin_credentials.username)
#
#         return "Incorrect email or password"
#
#     return "Incorrect email or password"
#
#
# @router.post("/admin_signup")
# def admin_signup(admin: AdminModel = Body(...)):
#     admin_exists = admin_collection.find_one({"email":  admin.email}, {"_id": 0})
#     if admin_exists:
#         return "Email already exists"
#
#     admin.password = hash_helper.encrypt(admin.password)
#     new_admin = add_admin(jsonable_encoder(admin))
#     return new_admin


@router.post("/user_login")
def user_login(user_credentials: HTTPBasicCredentials = Body(...)):
    user = user_collection.find_one({"email": user_credentials.username}, {"_id": 0})
    if user:
        password = hash_helper.verify(
            user_credentials.password, user["password"])
        if password:
            token, expires = signJWT(user_credentials.username)
            return {
                "obj_id": retrieve_user(email=user_credentials.username)['obj_id'],
                "email": user_credentials.username,
                "token": token,
                "expires": expires
            }

        raise HTTPException(status_code=404, detail="Incorrect email or password")

    raise HTTPException(status_code=404, detail="Incorrect email or password")


@router.post("/user_signup")
def user_signup(user: UserModel = Body(...)):
    user_exists = user_collection.find_one({"email": user.email}, {"_id": 0})
    if user_exists:
        raise HTTPException(status_code=404, detail="Email already exists")

    user.password = hash_helper.encrypt(user.password)
    new_user = add_user(jsonable_encoder(user))
    return new_user
