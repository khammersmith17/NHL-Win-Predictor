from fastapi import APIRouter

router = APIRouter()


@app.get('/games/{date}')
async def get_games(date:str):
    response = requests.get(f'https://api-web.nhle.com/v1/schedule/{date}').json()
    games = []
    for game in response.get('gameWeek')[0].get('games'):
        game_info = {}
        game_info.update({'gameID':game.get('id')})
        game_info.update({'awayTeam': game.get('awayTeam').get('abbrev')})
        game_info.update({'homeTeam': game.get('homeTeam').get('abbrev')})
        game_info.update({"time": game.get('startTimeUTC')})
        games.append(game_info)
    return games

@app.get('/score/{game_id}')
async def get_score(game_id: int):
    return {"game_id": game_id}

@app.get("key/?username={username}&password={password}")
async def get_api_key(username:str, password:str) -> dict:
    """
    TODO
    query username and password to get key
    if user exists, return API key
    else return 400
    """

    if api_key:
        return {}

    else:
        return {
            "Status": 400,
            "Message": "No user exists with these credentials"
        }

@app.post()
async def create_user(user_name:str, password:str):
    """
    TODO
    validate username and password
    generate API key
    create user
    """
    return {}
