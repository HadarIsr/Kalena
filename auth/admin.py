from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from passlib.context import CryptContext

from database.database import admin_collection, user_collection

security = HTTPBasic()
hash_helper = CryptContext(schemes=["bcrypt"])


async def validate_admin_login(credentials: HTTPBasicCredentials = Depends(security)):
    admin = admin_collection.find_one({"email": credentials.username})
    if admin:
        password = hash_helper.verify(credentials.password, admin['password'])
        if not password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        return True
    return False


async def validate_user_login(credentials: HTTPBasicCredentials = Depends(security)):
    user_login = user_collection.find_one({"email": credentials.username})
    if user_collection:
        password = hash_helper.verify(credentials.password, user_login['password'])
        if not password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        return True
    return False

