from pydantic import BaseModel
from typing import 

class TeamGame(BaseModel):
    '''
    Setting type to enforce the same schema as exists in each teams game table
    '''

    gameId: int
    team_name: str
    blockedShotsAttemptFor: float
    corsiPercentage: float
    dZoneGiveawaysFor: int
    faceOffsWonFor: int
    fenwickPercentage: float
    flurryAdjustedxGoalsFor: float
    flurryScoreVenueAdjustedxGoalsFor
    freezeFor
    giveawaysFor
    goalsAgainst
    highDangerGoalsFor
    highDangerShotsFor
    highDangerxGoalsFor
    hitsFor
    lowDangerGoalsFor
    lowDangerShotsFor
    lowDangerxGoalsFor
    mediumDangerGoalsFor
    mediumDangerShotsFor
    mediumDangerxGoalsFor
    missedShotsFor
    penalityMinutesFor
    penaltiesFor
    playContinuedInZoneFor
    playContinuedOutsideZoneFor
    playStoppedFor
    reboundGoalsFor
    reboundsFor
    reboundxGoalsFor
    savedShotsOnGoalFor
    savedUnblockedShotAttemptsFor
    scoreAdjustedShotsAttemptsFor
    scoreAdjustedTotalShotCreditFor
    scoreAdjustedUnblockedShotAttemptsFor
    scoreFlurryAdjustedTotalShotCreditFor
    scoreVenueAdjustedxGoalsFor
    shotAttemptsFor
    shotsOnGoalFor
    takeawaysFor
    totalShotCreditFor
    unblockedShotAttemptsFor
    xFreezeFor
    xGoalsFor
    xGoalsFromActualReboundsOfShotsFor
    xGoalsFromxReboundsOfShotsFor
    xGoalsPercentage
    xOnGoalFor
    xPlayContinuedInZoneFor
    xPlayContinuedOutsideZoneFor
    xPlayStoppedFor
    xReboundsFor


class ModelInput(BaseModel):
    __tablename__ = 'games'

    game_id = Column(Integer, primary_key=True)
    home_team_id = Column(Integer, ForeignKey=True)
    away_team_id = Column(Integer, ForeignKey=True)
    '''
    To do: add features determined useful from the model
    '''
