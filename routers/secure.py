from fastapi import APIRouter, Depends, status, Request
from secure_utils.secure_db_utils import delete_user
import requests, json

router = APIRouter()

@router.get('/games/prediction/{game_id}')
async def get_predictions(game_id:int):
    try:
        ##### get team data
        ##### use the model to predict the outcome
        pass
    except:
        return {
            'Status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Unable to generate predictions"
        }

@router.delete("/delete/?username={username}&password={password}")
async def delete_user(username:str, password: str, request: Request):
    result = delete_user(username, password, request.app.state.db)
    if result == 1:
        return {
            "statusCode": status.HTTP_200_OK,
            "message": f"Deleted user: {username}"
        }
    elif result == -1:
        return {
            "statusCode": status.HTTP_400_BAD_REQUEST,
            "message": "User does not exist"
        }
    else:
        return {
            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "user does not exist"
        }

@router.get("/game_ids/{date}")
def get_game_ids(date: str):
    try:
        response = requests.get(f"https://api-web.nhle.com/v1/schedule/{date}").json()
        games = response.get("gameWeek")[0].get("games")
        game_ids = [game.get("id") for game in games]

        return {
            "statusCode": status.HTTP_200_OK,
            "body": json.dumps(game_ids)
        }

    except:
        return {
            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Internal Error. Try request again"
        }

