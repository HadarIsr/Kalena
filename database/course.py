from bson import ObjectId, errors
from database.user import retrieve_user, update_user_data, UserNotFoundException
from database.event import EventNotFoundException
from database.database import courses_collection


class CourseNotFoundException(Exception):
    pass

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

# _____________________ Courses _________________________


def retrieve_all_courses():
    return [course_helper(course) for course in courses_collection.find()]    


def retrieve_course(course_id) -> dict:
    try:
        course = courses_collection.find_one({"_id": ObjectId(course_id)})
        return course_helper(course)
    except CourseNotFoundException as ex:
        raise ex
    except errors.InvalidId as ex:
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
    except errors.InvalidId as ex:
        raise ex

def search_courses_by_field(field_name, desc):
    try:
        courses = []
        for course in courses_collection.find({field_name : desc}).sort("semester", 1):
            courses.append(course_helper(course))
        return courses
    except CourseNotFoundException as ex:
        raise ex


def add_courses_to_user(user_id: str, courses_id: list):
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        for course_id in courses_id:
            if course_id in user['courses']:
                raise CourseNotFoundException(f"User {user_id} has register to this course {course_id}")
            else:
                user['courses'].append(course_id)

        update_user_data(user_id, user)

    except UserNotFoundException as ex:
        raise ex
    except errors.InvalidId as ex:
        raise ex

def delete_course(user_id: str, course_id: str):
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        if course_id in user['courses']:
            user['courses'].remove(course_id)
            update_user_data(user_id, user)

    except UserNotFoundException as ex:
        raise ex
    except errors.InvalidId as ex:
        raise ex

def delete_list_of_courses(user_id: str, courses_id: list):
    try:
        user = retrieve_user(_id=ObjectId(user_id))
        for course_id in courses_id:
            if course_id in user['courses']:
                user['courses'].remove(course_id)
            else:
                raise CourseNotFoundException
        update_user_data(user_id, user)

    except UserNotFoundException as ex:
        raise ex
    except errors.InvalidId as ex:
        raise ex
        
def fix_date():
    courses = retrieve_all_courses()
    for i in range(20, len(courses)):
        print(courses[i]['start_date'])

# def search_courses(**kwargs):
#     courses = []
#     for course in courses_collection.find(kwargs):
#         courses.append(course_helper(course))
#     return courses


# def add_courses():
#     wb = load_workbook(filename=PATH_TO_COURSES_EXCEL)
#     courses_excel = wb.active

#     last_column = len(list(courses_excel.columns))
#     last_row = len(list(courses_excel.rows))
#     for row in range(2, last_row + 1):
#         cur_course = {}
#         for column in range(1, last_column + 1):
#             column_letter = get_column_letter(column)
#             cur_course[courses_excel[column_letter + str(1)].value] = str(courses_excel[column_letter + str(row)].value)
#         courses_collection.insert_one(cur_course)


# def update_courses_name():
#     for course in courses_collection.find():
#         course['degree'] = str(course['degree']).replace('\xa0', ' ')
#         courses_collection.update_one({"_id": ObjectId(course['_id'])}, {"$set": course})
