USE NHL;
CREATE TABLE USERS(
	user_id INT NOT NULL,
	username VARCHAR(32) NOT NULL,
    password VARCHAR(32) NOT NULL,
    api_key VARCHAR(64) NOT NULL,
    PRIMARY KEY (user_id)
);

USE NHL;
CREATE TABLE GAME_PREDICTIONS(
	game_id INT NOT NULL,
    inference_score FLOAT NOT NULL,
    agg_method INT NOT NULL DEFAULT 10,
    PRIMARY KEY (game_id)
);

USE NHL;
CREATE TABLE GAME_OUTCOMES(
	game_id INT NOT NULL,
    home_team VARCHAR(32) NOT NULL,
    away_team VARCHAR(32) NOT NULL,
    home_team_score INT NOT NULL,
    away_team_score INT NOT NULL,
    game_date Date NOT NULL,
    PRIMARY KEY (game_id)
);

USE NHL;
CREATE TABLE TEAMS(
	team_id int NOT NULL,
    team_name VARCHAR(32) NOT NULL,
    team_code VARCHAR(5) NOT NULL,
    PRIMARY KEY (team_id)
);

USE NHL;
CREATE TABLE RAW_GAME_STATS(
	team_id int NOT NULL,
    game_date DATE NOT NULL,
    blockedShotAttemptsFor FLOAT NOT NULL,
    corsiPercentage FLOAT NOT NULL,
    dZoneGiveawaysFor FLOAT NOT NULL,
    faceOffsWonFor FLOAT NOT NULL,
    fenwickPercentage FLOAT NOT NULL,
    flurryAdjustedxGoalsFor FLOAT NOT NULL,
    flurryScoreVenueAdjustedxGoalsFor FLOAT NOT NULL,
    freezeFor FLOAT NOT NULL,
    giveawaysFor FLOAT NOT NULL,
    goalsAgainst FLOAT NOT NULL,
    highDangerGoalsFor FLOAT NOT NULL,
    highDangerShotsFor FLOAT NOT NULL,
    highDangerxGoalsFor FLOAT NOT NULL,
    hitsFor FLOAT NOT NULL,
	lowDangerGoalsFor INT NOT NULL,
    lowDangerShotsFor INT NOT NULL,
    lowDangerxGoalsFor FLOAT NOT NULL,
    mediumDangerGoalsFor INT NOT NULL,
    mediumDangerShotsFor INT NOT NULL,
    mediumDangerxGoalsFor FLOAT NOT NULL,
    missedShotsFor INT NOT NULL,
    penalityMinutesFor INT NOT NULL,
    penaltiesFor INT NOT NULL,
    playContinuedInZoneFor FLOAT NOT NULL,
    playContinuedOutsideZoneFor FLOAT NOT NULL,
    playStoppedFor FLOAT NOT NULL,
    reboundGoalsFor INT NOT NULL,
    reboundsFor INT NOT NULL,
    reboundxGoalsFor FLOAT NOT NULL,
    savedShotsOnGoalFor INT NOT NULL,
    savedUnblockedShotAttemptsFor INT NOT NULL,
    scoreAdjustedShotsAttemptsFor FLOAT NOT NULL,
    scoreAdjustedTotalShotCreditFor FLOAT NOT NULL,
    scoreAdjustedUnblockedShotAttemptsFor FLOAT NOT NULL,
    scoreFlurryAdjustedTotalShotCreditFor FLOAT NOT NULL,
    scoreVenueAdjustedxGoalsFor FLOAT NOT NULL,
    shotAttemptsFor INT NOT NULL,
    shotsOnGoalFor INT NOT NULL,
    takeawaysFor INT NOT NULL,
    totalShotCreditFor FLOAT NOT NULL,
    unblockedShotAttemptsFor INT NOT NULL,
    xFreezeFor FLOAT NOT NULL,
    xGoalsFor FLOAT NOT NULL,
    xGoalsFromActualReboundsOfShotsFor FLOAT NOT NULL,
    xGoalsFromxReboundsOfShotsFor FLOAT NOT NULL,
    xGoalsPercentage FLOAT NOT NULL,
    xOnGoalFor FLOAT NOT NULL,
    xPlayContinuedInZoneFor FLOAT NOT NULL,
    xPlayContinuedOutsideZoneFor FLOAT NOT NULL,
    xPlayStoppedFor FLOAT NOT NULL,
    xReboundsFor FLOAT NOT NULL
);

USE NHL;
CREATE TABLE AVG_GAME_STATS(
	team_id int NOT NULL,
    game_date DATE NOT NULL,
    write_date DATE NOT NULL,
    agg_method INT NOT NULL DEFAULT 10,
    blockedShotAttemptsFor FLOAT NOT NULL,
    corsiPercentage FLOAT NOT NULL,
    dZoneGiveawaysFor FLOAT NOT NULL,
    faceOffsWonFor FLOAT NOT NULL,
    fenwickPercentage FLOAT NOT NULL,
    flurryAdjustedxGoalsFor FLOAT NOT NULL,
    flurryScoreVenueAdjustedxGoalsFor FLOAT NOT NULL,
    freezeFor FLOAT NOT NULL,
    giveawaysFor FLOAT NOT NULL,
    goalsAgainst FLOAT NOT NULL,
    highDangerGoalsFor FLOAT NOT NULL,
    highDangerShotsFor FLOAT NOT NULL,
    highDangerxGoalsFor FLOAT NOT NULL,
    hitsFor FLOAT NOT NULL,
	lowDangerGoalsFor INT NOT NULL,
    lowDangerShotsFor INT NOT NULL,
    lowDangerxGoalsFor FLOAT NOT NULL,
    mediumDangerGoalsFor INT NOT NULL,
    mediumDangerShotsFor INT NOT NULL,
    mediumDangerxGoalsFor FLOAT NOT NULL,
    missedShotsFor INT NOT NULL,
    penalityMinutesFor INT NOT NULL,
    penaltiesFor INT NOT NULL,
    playContinuedInZoneFor FLOAT NOT NULL,
    playContinuedOutsideZoneFor FLOAT NOT NULL,
    playStoppedFor FLOAT NOT NULL,
    reboundGoalsFor INT NOT NULL,
    reboundsFor INT NOT NULL,
    reboundxGoalsFor FLOAT NOT NULL,
    savedShotsOnGoalFor INT NOT NULL,
    savedUnblockedShotAttemptsFor INT NOT NULL,
    scoreAdjustedShotsAttemptsFor FLOAT NOT NULL,
    scoreAdjustedTotalShotCreditFor FLOAT NOT NULL,
    scoreAdjustedUnblockedShotAttemptsFor FLOAT NOT NULL,
    scoreFlurryAdjustedTotalShotCreditFor FLOAT NOT NULL,
    scoreVenueAdjustedxGoalsFor FLOAT NOT NULL,
    shotAttemptsFor INT NOT NULL,
    shotsOnGoalFor INT NOT NULL,
    takeawaysFor INT NOT NULL,
    totalShotCreditFor FLOAT NOT NULL,
    unblockedShotAttemptsFor INT NOT NULL,
    xFreezeFor FLOAT NOT NULL,
    xGoalsFor FLOAT NOT NULL,
    xGoalsFromActualReboundsOfShotsFor FLOAT NOT NULL,
    xGoalsFromxReboundsOfShotsFor FLOAT NOT NULL,
    xGoalsPercentage FLOAT NOT NULL,
    xOnGoalFor FLOAT NOT NULL,
    xPlayContinuedInZoneFor FLOAT NOT NULL,
    xPlayContinuedOutsideZoneFor FLOAT NOT NULL,
    xPlayStoppedFor FLOAT NOT NULL,
    xReboundsFor FLOAT NOT NULL
);

