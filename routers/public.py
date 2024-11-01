from fastapi import APIRouter, HTTPException, status
from public_utils.public_data_models import NewUser
from public_utils.public_db_utils import  write_user
from db_enums import PatternConstraints
import re
import json
from datetime import datetime
import aiohttp


router = APIRouter()


@router.get('/v1/games/{date}')
async def get_games(date:str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api-web.nhle.com/v1/schedule/{date}') as resp:
                response = await resp.json()

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

@router.get("/v1/score/{game_id}")
async def get_score(game_id: str):
    pass


@router.get('/v1/scores/today')
async def get_scores_today():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api-web.nhle.com/v1/scoreboard/now") as resp:
                games = await resp.json()

        current_date = datetime.now().strftime("%Y-%m-%d")

        game_scores = []

        todays_games = None
        for day in games.get("gamesByDate"):
            if day.get("date") == current_date:
                todays_games = day.get("games")
                break

        assert todays_games is not None
        for game in todays_games:
            curr_game = {}
            curr_game.update({"game_id": game.get("id")})
            game_state = game.get("gameState")
            if game_state == "OFF":
                curr_game.update({"gameState": "notActive"})
                curr_game.update({"period": None})
            else:
                curr_game.update({"gameState": "active"})
                curr_game.update({"period": game.get("period")})
            curr_game.update(
                {
                    "homeTeam": {
                        "teamName": game.get("homeTeam").get("name").get("default"),
                        "score": game.get("homeTeam").get("score")
                    }
                }
            )
            curr_game.update(
                {
                    "awayTeam": {
                        "teamName": game.get("awayTeam").get("name").get("default"),
                        "score": game.get("awayTeam").get("score")
                    }
                }
            )

            game_scores.append(curr_game)
        return {
            "status": status.HTTP_200_OK,
            "body": {
                "games": game_scores
            }
        }

    except:
        return {
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "messages": "Error getting current scores"
        }


@router.put("/v1/create-user")
async def create_user(user_data: NewUser):
    """
    validate username and password
    if username or password is invalid, return a 400
    generate api key for the user
    pass args to create_user db method
    return the api key to user if successful,
    otherwise, if it is a db failure return 500
    """
    if not re.fullmatch(PatternConstraints.USERNAME_PATTERN.value, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Username did not meet requirements. Constraints: ^[0-9A-Za-z]{6,16}"
        )
    if not re.fullmatch(PatternConstraints.PASSWORD_PATTERN.value, user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Password did not meet requirements. Constraints: ^(?=.*?[0-9])(?=.*?[A-Za-z]).{8,32}"
        )

    db_status, api_key = await  write_user(username=user_data.username, 
                     password=user_data.password
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

@router.get("/game_ids/{date}")
async def get_game_ids(date: str):
    """
    check for valid datetime format
    make a request to the nhl api schedule endpoint for the date
    parse request and return schedule
    """
    try:
        assert datetime.strptime(date, "%Y-%m-%d")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api-web.nhle.com/v1/schedule/{date}") as resp:
                response = await resp.json()
        games = response.get("gameWeek")[0].get("games")
        game_ids = [
                {
                    "game_id": game.get("id"),
                    "awayTeam": game.get("awayTeam").get("placeName").get("default"),
                    "homeTeam": game.get("homeTeam").get("placeName").get("default")
                }
                for game in games]

        return {
            "statusCode": status.HTTP_200_OK,
            "body": json.dumps(game_ids)
        }

    except AssertionError:
        return {
            "statusCode": status.HTTP_400_BAD_REQUEST,
            "message": "Invalid datetime format. Accepted: %Y-%m-%d"
        }
    except Exception:
        return {
            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Internal Error. Try request again"
        }


