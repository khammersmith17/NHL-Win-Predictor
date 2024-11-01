from fastapi import APIRouter, status
from secure_utils.secure_db_utils import (
    delete_db_user,
    get_game_prediction_game_id,
    get_predictions_today
)
from db_enums import DB_STATUS
import aiohttp
from datetime import datetime

router = APIRouter()

@router.get("/v1/games/daily-predictions")
async def get_day_predictions():
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        predictions = get_predictions_today(date=today)
        if predictions is None:
            raise Exception

        return {
            "status": status.HTTP_200_OK,
            "body": predictions
        }
    except:
        return {
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Internal server error"
        }

@router.get('/v1/games/prediction/{game_id}')
async def get_predictions(game_id:str):
    try:
        score = get_game_prediction_game_id(game_id=game_id)

        if score is None:
            raise Exception
        if score < 0:
            return {
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "game id is invalid"
            }

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api-web.nhle.com/v1/gamecenter/{game_id}/boxscore") as resp:
                response = await resp.json()

        #TODO: parse response for teams

        home_team = ...
        away_team = ...
        body = {
            home_team: score,
            away_team: (1 - score)
        }
        return {
            "status": status.HTTP_200_OK,
            "body": body
        }
    except:
        return {
            'Status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Unable to generate predictions"
        }


@router.delete("/v1/delete/?username={username}&password={password}")
async def delete_user(username:str, password: str):
    result = delete_db_user(username, password)
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


