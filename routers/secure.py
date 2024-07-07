from fastapi import APIRouter, Depends



router = APIRouter()

@router.get('/games/prediction/{game_id}')
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
