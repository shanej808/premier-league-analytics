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

CREATE TABLE IF NOT EXISTS odds (
    match_id    INTEGER REFERENCES matches(match_id),
    home_odds   DOUBLE,
    draw_odds   DOUBLE,
    away_odds   DOUBLE
);
