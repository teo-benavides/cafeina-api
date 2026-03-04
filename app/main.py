from fastapi import FastAPI
from app.api import activity, cafe
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(activity.router, prefix="/activities", tags=["Activities"])
app.include_router(cafe.router, prefix="/cafes", tags=["Cafes"])