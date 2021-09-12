import ssl
from datetime import datetime, timedelta
from bson import ObjectId
import pymongo


MONGO_DETAILS = "mongodb+srv://kalena:10203040@cluster0.48shf.mongodb.net/calendar?retryWrites=true&w=majority"
client = pymongo.MongoClient(MONGO_DETAILS, ssl_cert_reqs=ssl.CERT_NONE)
database = client.kalena

user_collection = database.get_collection('users')
admin_collection = database.get_collection('admins')
event_collection = database.get_collection('events')
courses_collection = database.get_collection('courses')
holidays_collection = database.get_collection('jewish_holidays')

# _______________________ ADMIN _______________________

def admin_helper(admin) -> dict:
    return {
        "obj_id": str(admin['_id']),
        "fullname": admin['fullname'],
        "email": admin['email'],
    }

def add_admin(admin_data: dict) -> dict:
    admin = admin_collection.insert_one(admin_data)
    new_admin = admin_collection.find_one({"_id": admin.inserted_id})
    return admin_helper(new_admin)


def retrieve_admins():
    admins = []
    for cur_admin in admin_collection.find():
        admins.append(admin_helper(cur_admin))
    return admins

