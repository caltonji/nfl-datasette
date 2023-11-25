# These Commands are for setting up the DB. Not needed to run every time
import pandas as pd
import sqlite3
import nfl_data_py as nfl
seasons = [1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
df_schedules = nfl.import_schedules(seasons)
df_player_stats = nfl.import_weekly_data(seasons)

# fix oponent team
if "opponent_team" in df_player_stats:
    df_player_stats = df_player_stats.drop(columns="opponent_team")

df_schedules = df_schedules[['home_team', 'away_team', 'season', 'week']]
# Merge player_data with schedules on away_team
result_home = df_player_stats.merge(df_schedules,
                                left_on=['season', 'week', 'recent_team'],
                                right_on=['season', 'week', 'home_team'],
                                how='left').drop(columns="home_team").rename(columns={"away_team": "opponent_team"})
result_away = df_player_stats.merge(df_schedules,
                                left_on=['season', 'week', 'recent_team'],
                                right_on=['season', 'week', 'away_team'],
                                how='left').drop(columns="away_team").rename(columns={"home_team": "opponent_team"})
# Combine the results from both merges and fill missing values
df_player_stats = result_away.combine_first(result_home)

# Drop the POST season.  Doesn't matter for Fantasy
df_player_stats = df_player_stats[df_player_stats["season_type"] == "REG"]

drop_columns = ["player_name", "position_group", "headshot_url", "season_type", "passing_epa", "pacr", "dakota", "rushing_epa", "receiving_epa", "target_share", "air_yards_share", "racr", "wopr"]
df_player_stats = df_player_stats.drop(columns=drop_columns)

conn = sqlite3.connect('nfl.db')
df_player_stats.to_sql('players', conn, index=False, if_exists='replace')

conn.execute("""CREATE VIEW IF NOT EXISTS players_yearly AS
SELECT
    player_id,
    player_display_name,
    position,
    GROUP_CONCAT(DISTINCT recent_team) AS recent_teams,
    season,
    count(*) AS games_played,
    SUM(completions) AS completions,
    SUM(attempts) AS attempts,
    SUM(passing_yards) AS passing_yards,
    SUM(passing_tds) AS passing_tds,
    SUM(interceptions) AS interceptions,
    SUM(sacks) AS sacks,
    SUM(sack_yards) AS sack_yards,
    SUM(sack_fumbles) AS sack_fumbles,
    SUM(sack_fumbles_lost) AS sack_fumbles_lost,
    SUM(passing_air_yards) AS passing_air_yards,
    SUM(passing_yards_after_catch) AS passing_yards_after_catch,
    SUM(passing_first_downs) AS passing_first_downs,
    SUM(passing_2pt_conversions) AS passing_2pt_conversions,
    SUM(carries) AS carries,
    SUM(rushing_yards) AS rushing_yards,
    SUM(rushing_tds) AS rushing_tds,
    SUM(rushing_fumbles) AS rushing_fumbles,
    SUM(rushing_fumbles_lost) AS rushing_fumbles_lost,
    SUM(rushing_first_downs) AS rushing_first_downs,
    SUM(rushing_2pt_conversions) AS rushing_2pt_conversions,
    SUM(receptions) AS receptions,
    SUM(targets) AS targets,
    SUM(receiving_yards) AS receiving_yards,
    SUM(receiving_tds) AS receiving_tds,
    SUM(receiving_fumbles) AS receiving_fumbles,
    SUM(receiving_fumbles_lost) AS receiving_fumbles_lost,
    SUM(receiving_air_yards) AS receiving_air_yards,
    SUM(receiving_yards_after_catch) AS receiving_yards_after_catch,
    SUM(receiving_first_downs) AS receiving_first_downs,
    SUM(receiving_2pt_conversions) AS receiving_2pt_conversions,
    SUM(special_teams_tds) AS special_teams_tds,
    SUM(fantasy_points) AS fantasy_points,
    SUM(fantasy_points_ppr) AS fantasy_points_ppr
FROM players
GROUP BY player_id, player_display_name, position, season;""")

conn.close()
