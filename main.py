from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from routers import secure, public
from utils.data_loader import DataLoader
from http import HTTPStatus
from auth import auth_user
from db import db_instance
import redis

cache = dict()

@asynccontextmanager
async def lifespan(app: FastAPI):
    cache["redis"] = redis.Redis(host="localhost", port=6379, decode_responses=True)
    yield
    cache.clear()


app = FastAPI(
    title="NHL Win Predictor API",
    description="""
    Uses an XGBoost model and data from MoneyPuck.com.
    Includes some utils that leverage the public NHP API.
    Backend Database is postgres
    """,
    lifespan=lifespan
)

app.include_router(
    public.router,
    prefix="api/v1/public"
)

app.include_router(
    secure.router,
    prefix="api/v1/secure",
    dependencies=[Depends(auth_user)]
)





@app.get('/ping')
async def root():
    return {
                "Status" : HTTPStatus.OK.value,
                "message":"Succesful Ping"
            }



