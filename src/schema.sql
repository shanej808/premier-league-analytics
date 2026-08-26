CREATE TABLE IF NOT EXISTS raw_matches (
    season      VARCHAR,
    date        VARCHAR,
    home_team   VARCHAR,
    away_team   VARCHAR,
    fthg        INTEGER,
    ftag        INTEGER,
    ftr         VARCHAR,
    b365h       DOUBLE,
    b365d       DOUBLE,
    b365a       DOUBLE
);

CREATE TABLE IF NOT EXISTS teams (
    team_id     INTEGER PRIMARY KEY,
    team_name   VARCHAR UNIQUE
);

CREATE TABLE IF NOT EXISTS matches (
    match_id    INTEGER PRIMARY KEY,
    season      VARCHAR,
    match_date  DATE,
    home_team_id INTEGER REFERENCES teams(team_id),
    away_team_id INTEGER REFERENCES teams(team_id),
    home_goals  INTEGER,
    away_goals  INTEGER,
    result      VARCHAR
);

-- Columns below are the match-winner odds present across all three of the
-- currently-loaded seasons (2022-23, 2023-24, 2024-25) in the original
-- football-data.co.uk files: Bet365, Pinnacle, and the cross-bookmaker
-- average. Other bookmaker columns (e.g. Betfair, 1xBet) only appear in
-- some seasons and aren't captured here.
CREATE TABLE IF NOT EXISTS odds (
    match_id    INTEGER REFERENCES matches(match_id),
    b365h       DOUBLE,  -- Bet365 home win odds
    b365d       DOUBLE,  -- Bet365 draw odds
    b365a       DOUBLE,  -- Bet365 away win odds
    psh         DOUBLE,  -- Pinnacle home win odds
    psd         DOUBLE,  -- Pinnacle draw odds
    psa         DOUBLE,  -- Pinnacle away win odds
    avgh        DOUBLE,  -- market average home win odds
    avgd        DOUBLE,  -- market average draw odds
    avga        DOUBLE   -- market average away win odds
);
