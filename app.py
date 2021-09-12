from fastapi import FastAPI, Depends
from auth.jwt_bearer import JWTBearer
from routes.user import router as UserRouter
from routes.login import router as LoginRouter
from routes.event import router as EventRouter
from routes.friends import router as FriendsRouter
from routes.courses import router as CoursesRouter
from routes.meetings import router as MeetingsRouter
from routes.holidays import router as HolidaysRouter


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

token_listener = JWTBearer()

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app."}

#react.js support
origins = ['https://localhost:3000',
            'localhost:3000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = ['*'],
    allow_credentials =True,
    allow_methods = ['*'],
    allow_headers=['*'],
)


app.include_router(LoginRouter, tags=["Login"], prefix="/login")
app.include_router(UserRouter, tags=["Users"], prefix="/user", dependencies=[Depends(token_listener)])
app.include_router(EventRouter, tags=["Events"], prefix="/event", dependencies=[Depends(token_listener)])
app.include_router(FriendsRouter, tags=["Friends"], prefix="/friends", dependencies=[Depends(token_listener)])
app.include_router(CoursesRouter, tags=["Courses"], prefix="/courses", dependencies=[Depends(token_listener)])
app.include_router(MeetingsRouter, tags=["Meetings"], prefix="/meetings", dependencies=[Depends(token_listener)])
app.include_router(HolidaysRouter, tags=["Holidays"], prefix="/holidays", dependencies=[Depends(token_listener)])