from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Body
from passlib.context import CryptContext
from fastapi.encoders import jsonable_encoder
from database.course import CourseNotFoundException, UserNotFoundException, delete_course, retrieve_all_courses, retrieve_user_courses, retrieve_course,delete_list_of_courses, search_courses_by_field, add_courses_to_user
from models.event import ResponseModel, AddCourses
from bson import errors

router = APIRouter()
hash_helper = CryptContext(schemes=["bcrypt"])


@router.get("/get_all_courses")
def get_all_courses():
    courses = retrieve_all_courses()
    if len(courses) > 0:
        return ResponseModel(courses, "courses data retrieved successfully") 
    else:
        return ResponseModel(courses, "No courses")


@router.get("/get_all_user_courses/{user_id}")
def get_user_courses(user_id: str):
    try:
        courses = retrieve_user_courses(user_id)
        if len(courses) > 0:
            return ResponseModel(courses, "courses data retrieved successfully")
        else:
            return ResponseModel(courses, "No courses")
    except UserNotFoundException as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except errors.InvalidId as ex:
         raise HTTPException(status_code=404, detail=str(ex))

@router.get("/get_course/{course_id}")
def get_course(course_id: str):
    try:
        course = retrieve_course(course_id)
        return ResponseModel(course, "course data retrieved successfully")
    except CourseNotFoundException:
        raise HTTPException(status_code=404, detail="Course doesn't exist.")
    except errors.InvalidId as ex:
         raise HTTPException(status_code=404, detail=str(ex))

@router.get("/get_courses_by_field/{field}/{description}")
def get_courses_by_field(field: str, description: str):
    try:
        courses = search_courses_by_field(field, description)
        if len(courses) > 0:
            return ResponseModel(courses, "degree courses retrieved successfully") 
        else:
            return ResponseModel(courses, "No courses")
    except CourseNotFoundException:
        raise HTTPException(status_code=404, detail="Degree code doesn't exist.")
    except errors.InvalidId as ex:
         raise HTTPException(status_code=404, detail=str(ex))

@router.patch("/delete_course_from_user/{user_id}/{course_id}")
def delete_user_course(user_id: str, course_id: str):
    try:
        delete_course(user_id, course_id)
        return ResponseModel('delete', "User course successfully removed.")
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="User doesn't exist.")
    except CourseNotFoundException:
        raise HTTPException(status_code=404, detail="Course doesn't exist.")
    except errors.InvalidId as ex:
         raise HTTPException(status_code=404, detail=str(ex))

@router.patch("/delete_list_of_courses/{user_id}")
def delete_courses(user_id: str, courses_id_list: AddCourses = Body(...)):
    try:
        courses_id_list = jsonable_encoder(courses_id_list)
        delete_list_of_courses(user_id, courses_id_list["courses_list"])
        return ResponseModel('delete', "User courses successfully removed.")
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="User doesn't exist.")
    except CourseNotFoundException:
        raise HTTPException(status_code=404, detail="Course doesn't exist.")
    except errors.InvalidId as ex:
         raise HTTPException(status_code=404, detail=str(ex))

@router.patch("/add_courses_to_user/{user_id}")
def add_courses_to_the_user(user_id: str, courses_id_list: AddCourses = Body(...)):
    try:
        courses_id_list = jsonable_encoder(courses_id_list)
        add_courses_to_user(user_id, courses_id_list["courses_list"])
        return ResponseModel('success', "User courses added successfully.")
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="User doesn't exist.")
    except CourseNotFoundException as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except errors.InvalidId as ex:
         raise HTTPException(status_code=404, detail=str(ex))