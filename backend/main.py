from fastapi import FastAPI, Depends
from routers import secure, public
import requests
from multiprocessing import Process
from utils.data_loader import DataLoader
from http import HTTPStatus


app = FastAPI()

app.include_router(
    public.router,
    prefix="api/v1/public"
)

app.include_router(
    secure.router,
    prefix="api/v1/secure",
    dependencies=[Depends(get_user)]
)

@app.get('/')
async def root():
    return {
            "Status" : HTTPStatus.OK.value,
            "message":"Hello World"
            }


@app.get('/games/prediction/{game_id}')
async def get_predictions(game_id:int):
    try:
        ##### get team data
        ##### use the model to predict the outcome
        pass
    except:
        return {
            'Status':HTTPStatus.INTERNAL_SERVER_ERROR,
            "message": "Unable to generate predictions"
        }
