from datetime import datetime, timedelta
from bson import ObjectId, errors
from database.user import retrieve_user, UserNotFoundException, update_user_data
from database.friend import FriendNotFoundException
from database.database import event_collection

MAXIMUM_DAYS_IN_DATA_BASE = 30


class EventNotFoundException(Exception):
    pass

# _______________________ Events  _______________________


def event_helper(event) -> dict:
    return {
        "obj_id": str(event['_id']),
        "creator": event['creator'],
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


def retrieve_user_event(user_id: str, event_id: str) -> dict:
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        if event_id in user['events'] or event_id in user['invitees']:
            return retrieve_event(event_id)
        else:
            raise EventNotFoundException(f"Could not find event {event_id}")  
    except UserNotFoundException as ex:
        raise ex


def retrieve_user_events(user_id):
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        return [retrieve_event(event_id) for event_id in user['events']]
        # return [retrieve_user_event(user_id, event_id) for event_id in user['events']]
    except UserNotFoundException as ex:
        raise ex


def update_event_details(user_id: str, event_id: str, data: dict):
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        event = retrieve_event(event_id)
        event.pop("obj_id")
        if user["email"] in event["participants"] and len(user['participants']) == 1:
            if event:
                for key in data.keys():
                    if data[key]:
                        event[key] = data[key]
            event_collection.update_one({"_id": ObjectId(event_id)}, {"$set": event})
            return event
        else:
            raise EventNotFoundException(f"could not edit event data {event_id}")
    except errors.InvalidId as ex:
        raise ex


def update_event_data(event_id: str, data: dict):
    event = event_collection.find_one({"_id": ObjectId(event_id)})
    if event:
        event_collection.update_one({"_id": ObjectId(event_id)}, {"$set": data})
    else:
        raise EventNotFoundException(f"Could not find event {event_id}")


def invite_user_to_event(invited_user_mail: str, event_id: str):
    try:
        user_to_invite = retrieve_user(email=invited_user_mail)
        user_id = user_to_invite['obj_id']
        if event_id not in user_to_invite['invitees']:
            user_to_invite['invitees'].append(event_id)
            update_user_data(user_id, user_to_invite)
    except UserNotFoundException as ex:
        raise ex
    except errors.InvalidId as ex:
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
        update_user_data(user_id, user)
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
    except errors.InvalidId as ex:
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
    except errors.InvalidId as ex:
        raise ex


def retrieve_user_invitees_event(user_id: str):
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        return [retrieve_event(event_id) for event_id in user['invitees']
                if retrieve_event(event_id)]

    except UserNotFoundException as ex:
        raise ex
    except errors.InvalidId as ex:
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
            raise FriendNotFoundException(f"user {user_id} can not retrieve events from user {friend_id}")
    except UserNotFoundException as ex:
        raise ex
    except errors.InvalidId as ex:
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
                        update_user_data(user_id, user)
                event_collection.delete_one({"_id": ObjectId(event_id)})
            else:
                update_event_data(event_id, event)
        else:
            raise EventNotFoundException(f"user {user_id} can not delete this event {event_id}")

    except UserNotFoundException as ex:
        raise ex
    except errors.InvalidId as ex:
        raise ex


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
    except errors.InvalidId as ex:
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


def force_delete_event(event_id: str):
    event = retrieve_event(event_id)
    for user_email in (event['invitees'] + event['participants']):
        user = retrieve_user(email=user_email)
        if event_id in user['invitees']:
            user['invitees'].remove(event_id)
        if event_id in user['events']:
            user['events'].remove(event_id)
        update_user_data(user["obj_id"], user)
    event_collection.delete_one({"_id": ObjectId(event_id)})


# def delete_event_db():
#     events = event_collection.find({'creator': "hadar@mta.ac.il"})
#     for event in events:
#         event_collection.delete_one({"_id": ObjectId(event['_id'])})


def delete_all_events():
    events = retrieve_events()
    for event in events:
        force_delete_event(event['obj_id'])
