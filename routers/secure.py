from fastapi import APIRouter, Depends, status, Request
from secure_utils.secure_db_utils import delete_user
from db_enums import DB_STATUS
import requests, json
from datetime import datetime

router = APIRouter()

@router.get('/games/prediction/{game_id}')
async def get_predictions(game_id:int):
    try:
        if game_id == "all":
            # grab all game predictions
            pass
        else:
            #grab prediction for single game
            pass
    except:
        return {
            'Status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Unable to generate predictions"
        }


@router.delete("/delete/?username={username}&password={password}")
async def delete_user(username:str, password: str, request: Request):
    result = delete_user(username, password, request.app.state.db.connection)
    if result == DB_STATUS.SUCCESS:
        return {
            "statusCode": status.HTTP_200_OK,
            "message": f"Deleted user: {username}"
        }
    elif result == DB_STATUS.DELETE_FAILURE:
        return {
            "statusCode": status.HTTP_400_BAD_REQUEST,
            "message": "User does not exist"
        }
    else:
        return {
            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "user does not exist"
        }


