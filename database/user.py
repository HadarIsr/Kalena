from bson import ObjectId, errors
from database.database import user_collection

NOT_ALLOWED_TO_EDIT = ['obj_id', 'email']

class UserNotFoundException(Exception):
    pass


def create_new_user(user: dict) -> dict:
    user['city'] = ''
    user['address'] = ''
    user['events'] = []  # List of user's events obj_id
    user['invitees'] = []  # List of events to which the user has been invited
    user['courses'] = []   # List of courses that user registered
    user['friends'] = []  # List of user's friends obj_id
    user['requests'] = []  # List of user's friend request
    return user


def user_helper(user) -> dict:
    return {
        "obj_id": str(user['_id']),
        "email": user['email'],
        "first_name": user['first_name'],
        "last_name": user['last_name'],
        "city": user['city'],
        "address": user['address'],
        "degree": user['degree'],
        "events": user['events'],
        "invitees": user['invitees'],
        "courses": user['courses'],
        "friends": user['friends'],
        "requests": user['requests'],
    }


# _______________________ USER _______________________

def retrieve_users():
    users = []
    for cur_user in user_collection.find():
        users.append(user_helper(cur_user))
    return users


def retrieve_user(**kwargs):
    try:
        user = user_collection.find_one(kwargs)
        if user:
            return user_helper(user)
        else:
            raise UserNotFoundException(f"Could not find user {kwargs}")
    except errors.InvalidId as ex:
        raise ex

def add_user(user_data: dict) -> dict:
    user_data = create_new_user(user_data)
    user = user_collection.insert_one(user_data)
    new_user = user_collection.find_one({"_id": user.inserted_id})
    return user_helper(new_user)


def delete_user(**kwargs):
    try:
        user = user_collection.find_one(kwargs)
        if user:
            user_collection.delete_one(kwargs)
        else:
            raise UserNotFoundException(f"could not delete user {kwargs}")
    except errors.InvalidId as ex:
        raise ex


def update_user_details(user_id: str, data: dict):
    try:
        user = user_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            for key in data.keys():
                    if data[key]:
                        user[key] = data[key]

            user_collection.update_one({"_id": ObjectId(user_id)}, {"$set": user})
        else:
            raise UserNotFoundException(f"could not edit user data {user_id}")
    except errors.InvalidId as ex:
        raise ex


def update_user_data(user_id: str, data: dict):
    for field in NOT_ALLOWED_TO_EDIT:
        if field in data:
            data.pop(field)

    user = user_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        user_collection.update_one({"_id": ObjectId(user_id)}, {"$set": data})
    else:
        raise UserNotFoundException(f"could not edit user data {user_id}")


def clean_event_and_invitees():
    users = retrieve_users()
    for user in users:
        user['events'].clear()
        user['invitees'].clear()
        user['friends'].clear()
        update_user_data(user['obj_id'], user)