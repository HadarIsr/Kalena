import ssl
from datetime import datetime, timedelta
# import motor.motor_asyncio
from bson import ObjectId
# from decouple import config
import pymongo
#from models.user import ErrorResponseModel
from datetime import datetime, timedelta
from bson import ObjectId, errors

MAXIMUM_DAYS_IN_DATA_BASE = 30


MONGO_DETAILS = "mongodb+srv://kalena:10203040@cluster0.48shf.mongodb.net/calendar?retryWrites=true&w=majority"
# client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

#MONGO_DETAILS = "mongodb://kalena:10203040@cluster0.48shf.mongodb.net/calendar?retryWrites=true&w=majority"
client = pymongo.MongoClient(MONGO_DETAILS, ssl_cert_reqs=ssl.CERT_NONE)

database = client.kalena

user_collection = database.get_collection('users')
admin_collection = database.get_collection('admins')
event_collection = database.get_collection('events')
courses_collection = database.get_collection('courses')

MAXIMUM_DAYS_IN_DATA_BASE = 30

# _________________ Exeptions _________________________


class EventNotFoundException(Exception):
    pass


class UserNotFoundException(Exception):
    pass


class FriendNotFoundException(Exception):
    pass

class CourseNotFoundException(Exception):
    pass

# _________________ dict helpers ________________________


def user_helper(user) -> dict:
    return {
        "obj_id": str(user['_id']),
        "email": user['email'],
        # "password": user['password'],
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


def friend_helper(friend) -> dict:
    return {
        "first_name": friend['first_name'],
        "last_name": friend['last_name'],
        "email": friend['email'],
        "friends": friend['friends'],
        "degree": friend['degree']
    }


def admin_helper(admin) -> dict:
    return {
        "obj_id": str(admin['_id']),
        "fullname": admin['fullname'],
        "email": admin['email'],
    }


def event_helper(event) -> dict:
    return {
        "obj_id": str(event['_id']),
        "creator": str(event['creator']),
        "title": event['title'],
        "start_date": str(event['start_date']),
        "end_date": str(event['end_date']),
        "invitees": event['invitees'],
        "participants": event['participants'],
        "description": event['description'],
        "location": event['location'],
        "repeat": event['repeat'],
        "color": event['color'],
        "all_day": event['all_day']
    }

def course_helper(course) -> dict:
    return {
        "obj_id": str(course['_id']),
        "title": course['title'],
        "semester": course['semester'],
        "lecturer": course['lecturer'],
        "day": course['day'],
        "start_date": str(course['start_date']),
        "end_date": str(course['end_date']),
        "degree": course['degree'],
        "degree_code": course['degree_code']
    }


def delete_events_helper(event):
    return {
        "obj_id": str(event['_id']),
        "end_date": str(event['end_date']),
        "invitees": event['invitees'],
        "participants": event['participants'],
    }

# _______________________ ADMIN _______________________


def add_admin(admin_data: dict) -> dict:
    admin = admin_collection.insert_one(admin_data)
    new_admin = admin_collection.find_one({"_id": admin.inserted_id})
    return admin_helper(new_admin)


def retrieve_admins():
    admins = []
    for cur_admin in admin_collection.find():
        admins.append(admin_helper(cur_admin))
    return admins

# _______________________ USER _______________________


def retrieve_users():
    users = []
    for cur_user in user_collection.find():
        users.append(user_helper(cur_user))
    return users


def create_new_user(user: dict) -> dict:
    user['city'] = ''
    user['address'] = ''
    user['events'] = []  # List of user's events obj_id
    user['invitees'] = []  # List of events to which the user has been invited
    user['courses'] = []   # List of courses that user registered
    user['friends'] = []  # List of user's friends obj_id
    user['requests'] = []  # List of user's friend request
    return user


def add_user(user_data: dict) -> dict:
    user_data = create_new_user(user_data)
    user = user_collection.insert_one(user_data)
    new_user = user_collection.find_one({"_id": user.inserted_id})
    return user_helper(new_user)



def retrieve_user(**kwargs):
    user = user_collection.find_one(kwargs)
    if user:
        return user_helper(user)
    else:
        raise UserNotFoundException(f"Could not find user {kwargs}")


def delete_user(**kwargs):
    user = user_collection.find_one(kwargs)
    if user:
        user_collection.delete_one(kwargs)
    else:
        raise UserNotFoundException(f"could not delete user {kwargs}")


def update_user_details(user_id: str, data: dict):
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        for key in data.keys():
                if data[key]:
                    user[key] = data[key]

        user_collection.update_one({"_id": ObjectId(user_id)}, {"$set": user})
    else:
        raise UserNotFoundException(f"could not edit user data {user_id}")


def update_user_data(user_id: str, data: dict):
    not_allowed = ['obj_id', 'email']
    for field in not_allowed:
        if field in data:
            data.pop(field)

    user = user_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        user_collection.update_one({"_id": ObjectId(user_id)}, {"$set": data})
    else:
        raise UserNotFoundException(f"could not edit user data {user_id}")


# _______________________ FRIENDS SUPPORT _______________________

def retrieve_friend(user_id: str, friend_id: str) -> dict:
    try:
        friend = retrieve_user(_id=ObjectId(friend_id))
        if user_id in friend['friends']:
            return friend_helper(friend)
        else:
            raise UserNotFoundException(f"could not retrieve friend {friend_id}")
    except UserNotFoundException as ex:
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


def send_friend_request(sending_user_id: str, friend_receives_email: str):
    try:
        user = retrieve_user(_id=ObjectId(sending_user_id))
        friend = retrieve_user(email= friend_receives_email)
        friend_id = friend["obj_id"]
        if friend_id not in user['friends']:
        #if friend_receives_id not in user['friends']:
            if (sending_user_id not in friend['requests']) \
                    and (sending_user_id not in friend['friends']):
                friend['requests'].append(sending_user_id)
                update_user_data(friend_id, friend)
            else:
                raise FriendNotFoundException(f"The user sent friend request{sending_user_id}")
        else:
            raise FriendNotFoundException(f"The sender is friend of {friend_receives_email}")
    except UserNotFoundException as ex:
        raise ex


def decline_friend_request(user_id: str, user_declined_id: str):
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        if user_declined_id in user['requests']:
            user['requests'].remove(user_declined_id)
            update_user_data(user_id, user)
    except UserNotFoundException as ex:
        raise ex


def accept_friend_request(user_id: str, friend_id: str):
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        if friend_id in user['requests']:
            new_friend = retrieve_user(_id=ObjectId(friend_id))
            user['friends'].append(friend_id)
            new_friend['friends'].append(user_id)
            user['requests'].remove(friend_id)
            update_user_data(user_id, user)
            update_user_data(friend_id, new_friend)
        elif friend_id in user['friends']:
            raise FriendNotFoundException(f"friend {friend_id} already on {user_id} friends list ")
        else:
            raise FriendNotFoundException(f"user {user_id} do not have a friend request from {friend_id}")

    except UserNotFoundException as ex:
        raise ex


def retrieve_mutual_events(user_id: str, friend_id: str) -> list:
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        friend = retrieve_user(_id=ObjectId(friend_id))
        if user_id in friend['friends']:
            friend_events = set(friend['events'])
            mutual_events_id = [event_id for event_id in user['events'] if event_id in friend_events]
            mutual_events_lst = [retrieve_event(event_id) for event_id in mutual_events_id if event_id]
            return mutual_events_lst
        else:
            FriendNotFoundException(f"user {user_id} can not retrieve events from user {friend_id}")
    except UserNotFoundException as ex:
        raise ex


# _______________________ Events  _______________________

#
def retrieve_events():
    return [event_helper(event) for event in event_collection.find()]


def add_event(event_data: dict) -> dict:
    event = event_collection.insert_one(event_data)
    new_event = event_collection.find_one({"_id": event.inserted_id})
    return event_helper(new_event)


def retrieve_event(event_id: str) -> dict:
    event = event_collection.find_one({"_id": ObjectId(event_id)})
    if event:
        return event_helper(event)
    # else:
    #     raise EventNotFoundException(f"Could not find event {event_id}")


def retrieve_user_event(user_id: str, event_id: str) -> dict:
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        if event_id in user['events'] or event_id in user['invitees']:
            event = retrieve_event(event_id)
            if event:
                creator_id = event['creator']
                event['creator'] = retrieve_user(_id=ObjectId(creator_id))['email']
                if event['participants']:
                    participants = event['participants']
                    event['participants'] = [retrieve_user(_id=ObjectId(user_id))['email'] for user_id in participants]
                if event['invitees']:
                    invitees = event['invitees']
                    event['invitees'] = [retrieve_user(_id=ObjectId(user_id))['email'] for user_id in invitees]
                return event

    except UserNotFoundException as ex:
        raise ex


def retrieve_user_events(user_id):
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        return [retrieve_user_event(user_id, event_id) for event_id in user['events']]
    except UserNotFoundException as ex:
        raise ex


def update_event_details(user_id: str, event_id: str, data: dict):
    user = retrieve_user(_id=ObjectId(user_id))
    event = retrieve_event(event_id)
    if user["email"] in event["participants"]:
        if event:
            for key in data.keys():
                if data[key]:
                    event[key] = data[key]

        event_collection.update_one({"_id": ObjectId(event_id)}, {"$set": event})
        return event
    else:
        raise EventNotFoundException(f"could not edit event data {event_id}")


def update_event_data(event_id: str, data: dict):
    event = event_collection.find_one({"_id": ObjectId(event_id)})
    if event:
        event_collection.update_one({"_id": ObjectId(event_id)}, {"$set": data})
    else:
        raise EventNotFoundException(f"Could not find event {event_id}")


# def retrieve_user_event(user_id: str, event_id: str):
#     try:
#         user = retrieve_user(_id=ObjectId(user_id))
#         if event_id in user['events']:
#             return retrieve_event(event_id)
#         else:
#             raise EventNotFoundException(f"Could not find event {event_id}")
#     except UserNotFoundException as ex:
#         raise ex


def retrieve_all_user_events(user_id: str):
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        events = []
        for event_id in user['events']:
            event_details = retrieve_event(event_id)
            if event_details:
                events.append(event_details)
            else:
                user['events'].remove(event_id)
        update_user_data(user_id, user)
        return events

    except UserNotFoundException as ex:
        raise ex


def invite_user_to_event(invited_user_mail: str, event_id: str):
    try:
        user_to_invite = retrieve_user(email=invited_user_mail)
        user_id = user_to_invite['obj_id']
        if event_id not in user_to_invite['invitees']:
            user_to_invite['invitees'].append(event_id)
            update_user_data(user_id, user_to_invite)
        else:
            raise UserNotFoundException(f"user {invited_user_mail} is already invited to {event_id}")
    except UserNotFoundException as ex:
        raise ex
    except Exception as ex:
        raise ex


def add_repeat_event(events: list, event: dict, user: dict, user_id: str):
    if event['repeat'] == 'weekly':
        repeat_count = 12
        space = 1
    else:
        repeat_count = 4
        space = 4

    user_start_event = event['start_date'].split('T')
    user_end_event = event['end_date'].split('T')
    start_date = datetime.strptime(user_start_event[0], '%Y-%m-%d')
    end_date = datetime.strptime(user_end_event[0], '%Y-%m-%d')

    for _ in range(1, repeat_count):
        event.pop('obj_id')
        event = add_event(event)
        start_date += timedelta(days=(space * 7))
        end_date += timedelta(days=(space * 7))  # ++
        event['start_date'] = str(start_date.date()) + 'T' + user_start_event[1]
        event['end_date'] = str(end_date.date()) + 'T' + user_end_event[1]
        update_event_data(event['obj_id'], event)
        user['events'].append(event["obj_id"])
        events.append(event.copy())

    update_user_data(user_id, user)
    print(f'inside function\n: {events}\n')
    #return events


def add_event_to_users(user_id: str, event_data: dict) -> list:
    try:

        events = []
        user = retrieve_user(_id=ObjectId(user_id))
        if user["email"] not in event_data["participants"]:
            event_data['participants'].append(user["email"])
        retrieve_user(email=event_data['creator'])
        new_event = add_event(event_data)
        event_id = new_event['obj_id']
        events.append(new_event)
        user['events'].append(new_event["obj_id"])
        for invited_user_mail in new_event['invitees']:
            invite_user_to_event(invited_user_mail, event_id)
        if new_event['repeat'] == 'weekly' or new_event['repeat'] == 'monthly':
            add_repeat_event(events, new_event.copy(), user, user_id)
            print(f'outside function\n: {events}\n')
        update_user_data(user_id, user)
        #new_event = retrieve_event(event_id)
        for event1 in events:
            print(event1)
            print(event_helper(event1))
        return events
    except UserNotFoundException as ex:
        if event_id:
            force_delete_event(event_id)
        raise ex
    except errors.InvalidId as ex:
        raise ex


def accept_invite(user_id, event_id):
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        if event_id in user['invitees']:
            event = retrieve_event(event_id)
            if user["email"] in event['invitees']:
                user['invitees'].remove(event_id)
                user['events'].append(event_id)
                event['invitees'].remove(user["email"])
                event['participants'].append(user["email"])
                update_user_data(user_id, user)
                update_event_data(event_id, event)
            else:
                raise UserNotFoundException(f"user {user_id} not invitee to event {event_id}")
        else:
            raise EventNotFoundException(f"this event {event_id} not found in user {user_id} invitees")

    except EventNotFoundException as ex:
        raise ex
    except UserNotFoundException as ex:
        raise ex


def decline_invite(user_id, event_id):
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        event = retrieve_event(event_id)
        if user["email"] in event['invitees']:
            event['invitees'].remove(user["email"])
            update_event_data(event_id, event)
        if event_id in user['invitees']:
            user['invitees'].remove(event_id)
            update_user_data(user_id, user)
        

    except EventNotFoundException as ex:
        raise ex
    except UserNotFoundException as ex:
        raise ex


def retrieve_user_invitees_event(user_id: str):
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        return [retrieve_event(event_id) for event_id in user['invitees']
                if retrieve_event(event_id)]

    except UserNotFoundException as ex:
        raise ex


def retrieve_mutual_events(user_id: str, friend_id: str) -> list:
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        friend = retrieve_user(_id=ObjectId(friend_id))
        if user_id in friend['friends']:
            friend_events = set(friend['events'])
            mutual_events_id = [event_id for event_id in user['events'] if event_id in friend_events]
            mutual_events_lst = [retrieve_event(event_id) for event_id in mutual_events_id if event_id]
            return mutual_events_lst
        else:
            FriendNotFoundException(f"user {user_id} can not retrieve events from user {friend_id}")
    except UserNotFoundException as ex:
        raise ex


def delete_event(event_id: str, user_id: str):
    try:
        current_user = retrieve_user(_id=ObjectId(user_id))
        event = event_collection.find_one({"_id": ObjectId(event_id)})
        if current_user["email"] in event['participants']:
            event['participants'].remove(current_user["email"])
            if len(event['participants']) == 0:
                for user_email in event['invitees']:
                    user = retrieve_user(email=user_email)
                    if event_id in user['invitees']:
                        user['invitees'].remove(event_id)
                event_collection.delete_one({"_id": ObjectId(event_id)})
            else:
                update_event_data(event_id, event)
        else:
            raise EventNotFoundException(f"user {user_id} can not delete this event {event_id}")

    except UserNotFoundException as ex:
        raise ex


def force_delete_event(event_id: str):
    #event = retrieve_event(event_id)
    # for user_email in event['invitees']:
    #     user = retrieve_user(email=user_email)
    #     if user["email"] in event['participants']:
    #         if event_id in user['invitees']:
    #             user['invitees'].remove(event_id)
    #         if event_id in user['events']:
    #             user['events'].remove(event_id)
    event_collection.delete_one({"_id": ObjectId(event_id)})


def remove_user_event(user_id: str, event_id: str):
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        if event_id in user['events']:
            user['events'].remove(event_id)
            delete_event(event_id, user_id)
            update_user_data(user_id, user)
        else:
            raise EventNotFoundException(f"this event {event_id} not found in user {user_id} events")
    except UserNotFoundException as ex:
        raise ex

def delete_changes(event_id: str, user):
    if user:
        for key, val in user.items():
           if isinstance(val, dict):
                if event_id in val:
                    val.remove(event_id)
                    update_user_data(user["obj_id"], user)


def delete_old_events():
    last_date_in_data_base = datetime.today() - timedelta(days=MAXIMUM_DAYS_IN_DATA_BASE)
    events = retrieve_events()
    for event in events:
        if datetime(event['end_date']) < last_date_in_data_base:
            event_id = event['_id']
            for user_email in event['invitees'] + event['participants']:
                user = retrieve_user(email=user_email)
                delete_changes(event_id, user)


def delete_all_events():
    events = retrieve_events()
    for event in events:
        force_delete_event(event['obj_id'])

#     friends_list = ["612761a2f09892c80d114564", "6127b15c82eea7b134855f85", "6128c6e42cd908ef198539ad"]
#     meeting_time = 2.5
#     send_friend_request("612761a2f09892c80d114564", "t@t.com")
    
#     #meet_us(friends_list, meeting_time)

#    # b = retrieve_user(email=a[0]['email'])
#    #  chen_user = retrieve_user(_id=ObjectId(chen_id))
#    #  ronen_user = retrieve_user(_id=ObjectId(ronen_id))
#     #remove_user_event(test_id, event_id)
#    # algo_events = []
#     event_data = {
#         "creator": "612761a2f09892c80d114564",
#         "title": "try reapet monthly",
#         "start_date": "2021-09-02T10:15:00+00:00",
#         "end_date": "2021-09-02T14:15:00+00:00",
#         "invitees": [],
#         "participants": [],
#         "description": "check check",
#         "location": "telaviv",
#         "repeat": "monthly",
#         "color": "yellow",
#         "all_day": "False"
#     }
#     add_event_to_users(test_id_one, event_data)

#     #"degree_code": deg_code
#    # search_courses_by_field(degree_code= "CS")
#     strigi = "degree_code"
#     search_courses_by_field("degree_code" , "CS")
#     #courses = retrieve_user_courses(test_id)
#     #course = retrieve_course(course_id)
#     #findss = "BS"
#     #courses =[]
#  #   courses = retrieve_events()
#     #nee = []
#     #courses = search_courses_by_degree(findss)
#     #for course in courses:
#    #     nee.append(course["obj_id"])
#     #add_user_course(test_id, nee)

# #   test = retrieve_user(_id=ObjectId(test_id))
#    # add_event_to_users(test_id, event_data)
#     #event_data = retrieve_event(event_id)
#     #algo_events = user_relevant_events(test_id)
#     #update_user_data(test_id, test)
#     x = 2

# def retrieve_events():
#     return [event_helper(event) for event in event_collection.find()]


# def add_event(event_data: dict) -> dict:
#     event = event_collection.insert_one(event_data)
#     new_event = event_collection.find_one({"_id": event.inserted_id})
#     return event_helper(new_event)


# def retrieve_event(event_id: str) -> dict:
#     event = event_collection.find_one({"_id": ObjectId(event_id)})
#     if event:
#         return event_helper(event)
#     else:
#         raise EventNotFoundException(f"Could not find event {event_id}")


# def retrieve_user_event(user_id: str, event_id: str):
#     try:
#         user = retrieve_user(_id=ObjectId(user_id))
#         if event_id in user['events']:
#             event = retrieve_event(event_id)
#             return event
#     except UserNotFoundException as ex:
#         raise ex


# def delete_event(event_id: str, user_id: str):
#     try:
#         event = event_collection.find_one({"_id": ObjectId(event_id)})
#         if user_id in event['participants']:
#             event['participants'].remove(user_id)
#             if len(event['participants']) == 0:
#                 for user_id in event['invitees']:
#                     user = retrieve_user(_id=ObjectId(user_id))
#                     if event_id in user['invitees']:
#                         user['invitees'].remove(event_id)
#                 event_collection.delete_one({"_id": ObjectId(event_id)})
#             else:
#                 update_event_data(event_id, event)
#         else:
#             raise EventNotFoundException(f"user {user_id} can not delete this event {event_id}")
#     except EventNotFoundException as ex:
#         raise ex
#     except UserNotFoundException as ex:
#         raise ex


# def force_delete_event(event_id: str):
#     event = retrieve_event(event_id)
#     for user_id in event['invitees'] + event['participants']:
#         user = retrieve_user(_id=ObjectId(user_id))
#         if user:
#             if event_id in user['invitees']:
#                 user['invitees'].remove(event_id)
#             if event_id in user['events']:
#                 user['events'].remove(event_id)
#         event_collection.delete_one({"_id": ObjectId(event_id)})


# def update_event_details(user_id: str, event_id: str, data: dict):
#     event = retrieve_event(event_id)
#     if user_id in event["participants"]:
#         if event:
#             for key in data.keys():
#                 if data[key]:
#                     event[key] = data[key]

#         event_collection.update_one({"_id": ObjectId(event_id)}, {"$set": event})
#     else:
#         raise EventNotFoundException(f"could not edit event data {event_id}")


# def update_event_data(event_id: str, data: dict):
#     event = event_collection.find_one({"_id": ObjectId(event_id)})
#     if event:
#         event_collection.update_one({"_id": ObjectId(event_id)}, {"$set": data})
#     else:
#         raise EventNotFoundException(f"Could not find event {event_id}")


# def retrieve_all_user_events(user_id: str):
#     try:
#         user = retrieve_user(_id=ObjectId(user_id))
#         events = []
#         for event_id in user['events']:
#             event_details = retrieve_event(event_id)
#             if event_id:
#                 events.append(event_details)
#             else:
#                 user['events'].remove(event_id)
#         update_user_data(user_id, user)
#         return events

#     except UserNotFoundException as ex:
#         raise ex


# def invite_user_to_event(invited_user_id: str, event_id: str):
#     try:
#         user_to_invite = retrieve_user(_id=ObjectId(invited_user_id))
#         if event_id not in user_to_invite['invitees']:
#             user_to_invite['invitees'].append(event_id)
#             update_user_data(invited_user_id, user_to_invite)
#         else:
#             raise UserNotFoundException(f"user {invited_user_id} is not invitees")
#     except UserNotFoundException as ex:
#         raise ex

# #repeat
# def add_repeat_event(event: dict, user: dict, user_id: str) -> dict:
    
#     if event['repeat'] == 'weekly':
#         repeat_count = 12
#         space = 1
#     else:
#         repeat_count = 4
#         space = 4

#     user_start_event = event['start_date'].split('T')
#     user_end_event = event['end_date'].split('T')
#     start_date = datetime.strptime(user_start_event[0], '%Y-%m-%d')
#     end_date = datetime.strptime(user_end_event[0], '%Y-%m-%d')
#     event.pop('obj_id')
#     for x in range(1,repeat_count):
#         new_event = add_event(event)
#         start_date += timedelta(days=(space*7)) #++
#         new_event['start_date'] = str(start_date.date())+'T'+user_start_event[1]
#         new_event['end_date']= str(start_date.date())+'T'+user_end_event[1]
#         update_event_data(new_event['obj_id'], new_event)
#         user['events'].append(new_event["obj_id"])
#         update_user_data(user_id, user)


# def add_event_to_users(user_id: str, event_data: dict) -> dict:
#     try:
#         user = retrieve_user(_id=ObjectId(user_id))
#         if user_id not in event_data["participants"]:
#             event_data['participants'].append(user_id)
#         new_event = add_event(event_data)
#         user['events'].append(new_event["obj_id"])
#         if new_event['repeat'] == 'weekly' or new_event['repeat'] == 'monthly':
#             add_repeat_event(new_event, user, user_id)
#         for invited_user_id in new_event['invitees']:
#             invite_user_to_event(invited_user_id, new_event["obj_id"])
#         update_user_data(user_id, user)
#         return new_event
#     except UserNotFoundException as ex:
#         force_delete_event(new_event['obj_id'])
#         raise ex


# def accept_invite(user_id, event_id):
#     try:
#         user = retrieve_user(_id=ObjectId(user_id))
#         if event_id in user['invitees']:
#             event = retrieve_event(event_id)
#             if user_id in event['invitees']:
#                 user['invitees'].remove(event_id)
#                 user['events'].append(event_id)
#                 event['invitees'].remove(user_id)
#                 event['participants'].append(user_id)
#                 update_user_data(user_id, user)
#                 update_event_data(event_id, event)
#             else:
#                 raise UserNotFoundException(f"user {user_id} not invitee to event {event_id}")
#         else:
#             raise EventNotFoundException(f"this event {event_id} not found in user {user_id} invitees")

#     except EventNotFoundException as ex:
#         raise ex
#     except UserNotFoundException as ex:
#         raise ex


# def decline_invite(user_id, event_id):
#     try:
#         user = retrieve_user(_id=ObjectId(user_id))
#         event = retrieve_event(event_id)
#         if event_id in user['invitees']:
#             user['invitees'].remove(event_id)
#             update_user_data(user_id, user)
#         if user_id in event['invitees']:
#             event['invitees'].remove(user_id)
#             update_event_data(event_id, event)

#     except EventNotFoundException as ex:
#         raise ex
#     except UserNotFoundException as ex:
#         raise ex


# def remove_user_event(user_id, event_id: str):
#     try:
#         user = retrieve_user(_id=ObjectId(user_id))
#         if event_id in user['events']:
#             user['events'].remove(event_id)
#             delete_event(event_id, user_id)
#             update_user_data(user_id, user)
#         else:
#             raise EventNotFoundException(f"this event {event_id} not found in user {user_id} events")
#     except UserNotFoundException as ex:
#         raise ex


# def retrieve_user_invitees_event(user_id: str):
#     try:
#         user = retrieve_user(_id=ObjectId(user_id))
#         return [retrieve_event(event_id) for event_id in user['invitees']]

#     except EventNotFoundException as ex:
#         raise ex
#     except UserNotFoundException as ex:
#         raise ex


# def delete_old_events():
#     last_date_in_data_base = datetime.today() - timedelta(days=MAXIMUM_DAYS_IN_DATA_BASE)
#     events = retrieve_events()
#     for event in events:
#         if datetime(event['end_date']) < last_date_in_data_base:
#             event_id = event['_id']
#             users_relevant = event['invitees'] + event['participants']
#             for user_id in users_relevant:
#                 user = retrieve_user(_id=ObjectId(user_id))
#                 if user:
#                     for key, val in user.items():
#                         if isinstance(val, dict):
#                             if event_id in val:
#                                 val.remove(event_id)
#                                 update_user_data(user_id, user)


# _____________________ courses _________________________

def retrieve_all_courses():
    return [course_helper(course) for course in courses_collection.find()]


def retrieve_course(course_id) -> dict:
    course = courses_collection.find_one({"_id": ObjectId(course_id)})
    if course:
        return course_helper(course)
    else:
        raise CourseNotFoundException(f"Could not find course {course_id}")


def search_courses_by_field(field_name, desc):
    courses = []
    for course in courses_collection.find({field_name : desc}):
        courses.append(course_helper(course))
    return courses


def add_courses_to_user(user_id: str, courses_id: list):
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        for course_id in courses_id:
            if course_id in user['courses']:
                raise CourseNotFoundException(f"User {user_id} has register to this course")
            else:
                retrieve_course(course_id)
                user['courses'].append(course_id)
        update_user_data(user_id, user)

    except UserNotFoundException as ex:
        raise ex


def delete_course(user_id: str, course_id: str):
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        if course_id in user['courses']:
            user['courses'].remove(course_id)
            update_user_data(user_id, user)

    except UserNotFoundException as ex:
        raise ex


def retrieve_user_courses(user_id: str):
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        courses = []
        for course_id in user['courses']:
            course = retrieve_course(course_id)
            if course:
                courses.append(course)
        return courses
    except UserNotFoundException as ex:
        raise ex


def fix_date():
    courses = retrieve_all_courses()
    for i in range(20, len(courses)):
        course = courses[i]
        start_time = course['start_date']
        start_time = start_time.split('T')
        year, month, day = start_time[0].split('-')
        day, month = month, day
        course['start_date'] = year + '-' + month + '-' + day + 'T' + start_time[1]
        end_time = course['end_date']
        end_time = end_time.split('T')
        year, month, day = end_time[0].split('-')
        day, month = month, day
        course['end_date'] = year + '-' + month + '-' + day + 'T' + start_time[1]
        obj_id = course.pop('obj_id')
        # courses_collection.update_one({"_id": ObjectId(obj_id)}, {"$set": course})
        a=3


def delete_user_events(user_email):
    user = retrieve_user(email=user_email)
    for event in user['events']:
        force_delete_event(event)
    user['events'] = []
    update_user_data(user['obj_id'], user)




if __name__ == '__main__':
    delete_user_events('hadar@mta.ac.il')

