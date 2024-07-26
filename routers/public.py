from fastapi import APIRouter, HTTPException, status, Request
from public_utils.public_data_models import NewUser
from public_utils.public_db_utils import (
    PatternConstraints,
    write_user)
import re
import requests
import json


router = APIRouter()


@router.get('/games/{date}')
async def get_games(date:str):
    try:
        response = requests.get(f'https://api-web.nhle.com/v1/schedule/{date}').json()
        games = []
        for game in response.get('gameWeek')[0].get('games'):
            game_info = {}
            game_info.update({'gameID':game.get('id')})
            game_info.update({'awayTeam': game.get('awayTeam').get('abbrev')})
            game_info.update({'homeTeam': game.get('homeTeam').get('abbrev')})
            game_info.update({"time": game.get('startTimeUTC')})
            games.append(game_info)

        return {
            "statusCode": 200,
            "body": json.dumps({"games": games})
        } 
    except:
        return {
            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Error in the server"
        }

@router.get('/score/{game_id}')
async def get_score(game_id: int):
    games = requests.get().json()

    return {"game_id": game_id}


@router.post("/create-user")
async def create_user(user_data: NewUser, request: Request):
    if not re.fullmatch(PatternConstraints.USERNAME_PATTERN.value, user_data.username):
        raise HTTPException(
            status=status.HTTP_400_BAD_REQUEST, 
            detail="Username did not meet requirements. Constraints: ^[0-9A-Za-z]{6,16}"
        )
    if not re.fullmatch(PatternConstraints.PASSWORD_PATTERN.value, user_data.password):
        raise HTTPException(
            status=status.HTTP_400_BAD_REQUEST, 
            detail="Password did not meet requirements. Constraints: ^(?=.*?[0-9])(?=.*?[A-Za-z]).{8,32}"
        )

    db_status, api_key = await write_user(username=user_data.username, 
                     password=user_data.password, 
                     connection=request.app.state.db
                    )
    if db_status == 1:
        return {
            "status": status.HTTP_200_OK,
            "body": json.dumps({"api_key": api_key})
        }
    else:
        return {
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Internal error"
        }

