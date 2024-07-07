from fastapi import FastAPI, Depends
from routers import secure, public
from utils.data_loader import DataLoader
from http import HTTPStatus
from auth import auth_user
from db import db_instance
from inference import model


app = FastAPI(
    title="NHL Win Predictor API",
    description="""
    Uses an XGBoost model and data from MoneyPuck.com.
    Includes some utils that leverage the public NHP API.
    Backend Database is postgres
    """
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


@app.on_event("startup")
async def startup():
    await db_instance.connect()
    app.state.db = db_instance

    await model.get_model()
    app.state.model = model

@app.get('/')
async def root():
    return {
            "Status" : HTTPStatus.OK.value,
            "message":"Succesful Ping"
            }



