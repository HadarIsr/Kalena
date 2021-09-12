from datetime import date, datetime
from database.database import holidays_collection

class HolidaysNotFoundException(Exception):
    pass

THIS_YEAR = str(date.today().year)

def holiday_helper(holiday) -> dict:
    return {
        "obj_id": str(holiday['_id']),
        "title": holiday['Subject'],
        "start_date": str(datetime.strptime(holiday['Start Date'], '%d/%m/%Y')),
        "all_day": bool(holiday['All day event']),
        "description": str(holiday['Description']) 
    }

# _____________________ HOLIDAYS _________________________


def retrieve_holidays():
    #return [holiday_helper(holiday) for holiday in holidays_collection.find()]    
    year_query = {"Start Date" : {"$regex" : THIS_YEAR}}
    return [holiday_helper(holiday) for holiday in holidays_collection.find(year_query)]


def search_holidays_by_field(field_name, desc):
    try:
        holidays = []
        for holiday in holidays_collection.find({field_name : desc}):
            holidays.append(holiday_helper(holiday))
        return holidays
    except HolidaysNotFoundException:
        raise(f"could not find holiday data")

