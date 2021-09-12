import datetime
from datetime import timedelta
from database.user import UserNotFoundException, retrieve_user
from database.event import retrieve_user_events
from database.course import retrieve_user_courses
from bson import errors

QUARTER_HOUR = 15
THREE_QUARTETS = 45
DEFAULT_START_HOUR = 9.0
START_DAY = datetime.time(9, 0)
DEFAULT_END_HOUR = 22.0
END_DAY = datetime.time(22, 0)
DAYS_IN_WEEK = 7
MINUTES_IN_HOUR = 60
MEETING_PER_DAY = 26


def check_relevant_time_and_date(relevant_events: list, event: dict, start: datetime, end: datetime):
    user_start_event = event['start_date'].split('+')
    user_end_event = event['end_date'].split('+')
    start_date_time = datetime.datetime.strptime(user_start_event[0], '%Y-%m-%dT%H:%M:%S')
    end_date_time = datetime.datetime.strptime(user_end_event[0], '%Y-%m-%dT%H:%M:%S')

    if start_date_time.minute == QUARTER_HOUR or start_date_time.minute == THREE_QUARTETS:
        start_date_time -= timedelta(minutes=QUARTER_HOUR)
    if end_date_time.minute == QUARTER_HOUR or end_date_time.minute == THREE_QUARTETS:
        end_date_time += timedelta(minutes=QUARTER_HOUR)

    if start_date_time.date() == end_date_time.date():  # one day event
        if start.date() <= start_date_time.date() and end.date() >= end_date_time.date():
            relevant_events.append((start_date_time.strftime('%a'), start_date_time.time(), end_date_time.time()))
    elif start.date() <= start_date_time.date():  # An event that lasts over one day
        relevant_events.append((start_date_time.strftime('%a'), start_date_time.time(), datetime.time(22, 0)))
        start_date_time += timedelta(days=1)  # ++
        while start_date_time.date() != end_date_time.date() and start_date_time.date() <= end.date():
            relevant_events.append((start_date_time.strftime('%a'), START_DAY, END_DAY))
            start_date_time += timedelta(days=1)
        if start_date_time.date() == end_date_time.date() and start_date_time.date() <= end.date():
            relevant_events.append((start_date_time.strftime('%a'), START_DAY, end_date_time.time()))


def user_relevant_events(user_id: str) -> list:
    try:
        relevant_events = []
        start = datetime.datetime.now()
        end = start + timedelta(days=DAYS_IN_WEEK)
        user_events = retrieve_user_events(user_id)
        user_courses = retrieve_user_courses(user_id)

        if user_courses:
            for course in user_courses:
                check_relevant_time_and_date(relevant_events, course, start, end)
        if user_events:
            for event in user_events:
                check_relevant_time_and_date(relevant_events, event, start, end)

        return relevant_events

    except UserNotFoundException as ex:
        raise ex


def get_str_hour_to_int(hour: str) -> float:
    h = hour.hour
    m = hour.minute
    return int(h) + int(m)/MINUTES_IN_HOUR


def get_calendar_index(event: tuple) -> tuple:
    day_helper = {'Sun': 0, 'Mon': 1, 'Tue': 2, 'Wed': 3, 'Thu': 4, 'Fri': 5, 'Sat': 6}
    day, start, end = event
    day_index = day_helper[day]
    start_hour = get_str_hour_to_int(start)
    end_hour = get_str_hour_to_int(end)
    start_index = int(2*(max(start_hour, DEFAULT_START_HOUR) - DEFAULT_START_HOUR))
    end_index = int(2*(min(end_hour, DEFAULT_END_HOUR) - DEFAULT_START_HOUR))

    return day_index, start_index, end_index

    
def fill_calendar_in_events(users_id) -> tuple:
    calendar = [[True for i in range(MEETING_PER_DAY)] for j in range(DAYS_IN_WEEK)]

    for user_id in users_id:
        events = user_relevant_events(user_id)
        for event in events:
            day, start_hour, end_hour = get_calendar_index(event)
            for i in range(start_hour, end_hour):
                calendar[day][i] = False

    return calendar


def meet_us(users_email: list, meeting_time: float):
    try:
        users_id = [retrieve_user(email=user_email)['obj_id'] for user_email in users_email]
        day_helper = {0: 'Sun', 1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat'}
        meeting_time = int(meeting_time * 2) # We divided the day for half hour meeting
        calendar = fill_calendar_in_events(users_id)
        meeting = []
        for day in range(DAYS_IN_WEEK):
            for hour in range(MEETING_PER_DAY-meeting_time):
                available_time = True
                for i in range(meeting_time):
                    available_time = calendar[day][hour+i] and available_time
                if available_time:
                    meeting.append((day_helper[day], 0.5 * hour + 9, 0.5 * (hour + i + 1) + 9))
        return meeting

    except UserNotFoundException as ex:
        raise ex
    except errors.InvalidId as ex:
        raise ex