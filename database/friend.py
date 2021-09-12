from bson import ObjectId, errors
from database.user import retrieve_user, UserNotFoundException, update_user_data


class FriendNotFoundException(Exception):
    pass

# _______________________ FRIENDS SUPPORT _______________________


def friend_helper(friend) -> dict:
    return {
        "obj_id": friend['obj_id'],
        "first_name": friend['first_name'],
        "last_name": friend['last_name'],
        "email": friend['email'],
        "friends": friend['friends'],
        "degree": friend['degree']
    }


def retrieve_friend(friend_id: str) -> dict:
    try:
        friend = retrieve_user(_id=ObjectId(friend_id))
        return friend_helper(friend)
    except UserNotFoundException as ex:
        raise UserNotFoundException(f"could not retrieve friend {friend_id}")
    except errors.InvalidId as ex:
        raise ex

def get_friends_list(user_id: str) -> dict:
    try:
        friends = []
        user = retrieve_user(_id=ObjectId(user_id))
        for friend in user['friends']:
            friends.append(retrieve_friend(friend))
        return friends
    except UserNotFoundException as ex:
        raise UserNotFoundException(f"could not retrieve friend {friend}")
    except errors.InvalidId as ex:
        raise ex

def delete_friend(user_id: str, delete_friend_id: str):
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        friend_to_delete = retrieve_user(_id=ObjectId(delete_friend_id))
        if delete_friend_id in user['friends']:
            user['friends'].remove(delete_friend_id)
            update_user_data(user_id, user)
        if user_id in friend_to_delete['friends']:
            friend_to_delete['friends'].remove(user_id)
            update_user_data(delete_friend_id, friend_to_delete)
    except UserNotFoundException as ex:
        raise ex
    except errors.InvalidId as ex:
        raise ex

def retrieve_friends_request(user_id: str):
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        friends_request = []
        for req_id in user['requests']:
            user_req = retrieve_user(_id=ObjectId(req_id))
            friends_request.append(friend_helper(user_req))
        return friends_request
    except UserNotFoundException as ex:
        raise ex
    except errors.InvalidId as ex:
        raise ex

def send_friend_request(sending_user_id: str, friend_receives_email: str):
    try:
        user = retrieve_user(_id=ObjectId(sending_user_id))
        friend = retrieve_user(email=friend_receives_email)
        if user['email'] == friend_receives_email:
            raise UserNotFoundException("This users are friends")
        friend_id = friend["obj_id"]
        if friend_id not in user['friends']:
            if (sending_user_id not in friend['requests']) \
                    and (sending_user_id not in friend['friends']):
                friend['requests'].append(sending_user_id)
                update_user_data(friend_id, friend)
            else:
                raise FriendNotFoundException(f"The user has already submitted a friend request")
        else:
            raise FriendNotFoundException(f"Users are already friends")
    except UserNotFoundException as ex:
        raise ex
    except errors.InvalidId as ex:
        raise ex

def decline_friend_request(user_id: str, user_declined_id: str):
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        if user_declined_id in user['requests']:
            user['requests'].remove(user_declined_id)
            update_user_data(user_id, user)
    except UserNotFoundException as ex:
        raise ex
    except errors.InvalidId as ex:
        raise ex

def accept_friend_request(user_id: str, friend_id: str):
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        if friend_id in user['requests']:
            new_friend = retrieve_user(_id=ObjectId(friend_id))
            user['friends'].append(friend_id)
            new_friend['friends'].append(user_id)
            user['requests'].remove(friend_id)
            if user_id in new_friend['requests']:
                new_friend['requests'].remove(user_id)
            update_user_data(user_id, user)
            update_user_data(friend_id, new_friend)
        elif friend_id in user['friends']:
            raise FriendNotFoundException (f"friend {friend_id} already on {user_id} friends list ")
        else:
            raise FriendNotFoundException(f"user {user_id} do not have a friend request from {friend_id}")

    except UserNotFoundException as ex:
        raise ex
    except errors.InvalidId as ex:
        raise ex