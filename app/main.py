from fastapi import FastAPI
from app.api import activity, auth, cafe, me, user
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI()

origins = settings.CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(activity.router)
app.include_router(cafe.router)
app.include_router(auth.router)
app.include_router(me.router)
app.include_router(user.router)