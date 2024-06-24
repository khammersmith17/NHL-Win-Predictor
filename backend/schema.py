from pydantic import BaseModel

class PlayerBase(BaseModel):
    pass 

class PlayerCreate(PlayerBase):
    pass 

class TeamBase(BaseModel):
    pass 

class TeamCreate(TeamBase):
    pass 

class GameBase(BaseModel):
    pass 

class GameCreate(GameBase):
    pass 

class Player(PlayerBase):
    pass 

    class config:
        orm_mode = True

class Game(GameBase):
    pass 

    class config:
        orm_mode = True
