CREATE SCHEMA `serene-build.nba_player_stats`
OPTIONS (
    description = "Dataset containing NBA player statistics, game logs, and related data.",
    default_table_expiration_ms = NULL
);

CREATE TABLE `serene-build.nba_player_stats.players` (
    player_id INT64 NOT NULL, -- Unique identifier for players
    first_name STRING NOT NULL, -- Player's first name
    last_name STRING NOT NULL -- Player's last name
);

CREATE TABLE `serene-build.nba_player_stats.game_logs` (
    game_log_id INT64 NOT NULL, -- Unique identifier for each game log
    player_id INT64 NOT NULL, -- Reference to Players table
    season STRING NOT NULL, -- Season of the game (e.g., "2023-24")
    game_date DATE NOT NULL, -- Date of the game
    team STRING NOT NULL, -- Team of the player
    opponent STRING NOT NULL, -- Opponent team
    game_result STRING NOT NULL, -- Win or Loss ('W' or 'L')
    minutes INT64 NOT NULL, -- Minutes played
    pts INT64 NOT NULL, -- Points scored
    fgm INT64 NOT NULL, -- Field Goals Made
    fga INT64 NOT NULL, -- Field Goals Attempted
    fg_pct FLOAT64 NOT NULL, -- Field Goal Percentage
    fg3m INT64 NOT NULL, -- Three-Point Field Goals Made
    fg3a INT64 NOT NULL, -- Three-Point Field Goals Attempted
    fg3_pct FLOAT64 NOT NULL, -- Three-Point Field Goal Percentage
    ftm INT64 NOT NULL, -- Free Throws Made
    fta INT64 NOT NULL, -- Free Throws Attempted
    ft_pct FLOAT64 NOT NULL, -- Free Throw Percentage
    reb INT64 NOT NULL, -- Total Rebounds
    ast INT64 NOT NULL, -- Assists
    stl INT64 NOT NULL, -- Steals
    blk INT64 NOT NULL, -- Blocks
    tov INT64 NOT NULL, -- Turnovers
    pf INT64 NOT NULL -- Personal Fouls
);


