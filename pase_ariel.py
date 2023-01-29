from nba_api.stats.endpoints import boxscoreadvancedv2
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
import numpy as np
import pandas as pd

def get_pace_by_game_id_and_team_id(game_id, team_id):
    out = boxscoreadvancedv2.BoxScoreAdvancedV2(game_id=game_id)

    teams_id_2 = out.team_stats.data['data'][1][1]
    location = 0
    if teams_id_2 == team_id:
        location = 1
    pace = out.team_stats.data['data'][location][25]
    print(pace)
    return pace


def generate_ds_pace():
    nba_teams = teams.get_teams()
    all_teams_id = [val['id'] for val in nba_teams]
    for team_id in all_teams_id:
        # Query for games where the Celtics were playing
        gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id)
        # The first DataFrame of those returned is what we want.
        team_games = gamefinder.get_data_frames()[0]
        season_game_id_df = team_games[['SEASON_ID', 'GAME_ID', 'TEAM_NAME', 'TEAM_ID']]
        season_game_id_df.loc[:, "PACE"] = season_game_id_df.apply(lambda row:
                                                                   get_pace_by_game_id_and_team_id(row['GAME_ID'],
                                                                                                   row['TEAM_ID']),
                                                                   axis=1)

        print('hi')


def main():
    out = boxscoreadvancedv2.BoxScoreAdvancedV2(game_id='0022200742')
    print(out)
    pace_1 = out.team_stats.data['data'][0][25]
    pace_2 = out.team_stats.data['data'][1][25]


if __name__ == '__main__':
    from statsmodels.tsa.stattools import grangercausalitytests

    # Generate sample data
    data = {'T': [1, 2, 3, 4, 5, 6], 'Y': [2, 3, 4, 5, 6, 7]}
    df = pd.DataFrame(data)

    # Perform Granger causality test
    granger_test = grangercausalitytests(df[['Y', 'T']], maxlag=2)

    # Print results
    for i, test_results in enumerate(granger_test.items()):
        print("\nGranger causality test for lag={}".format(i + 1))
        print("\n".join("{}: {}".format(k, v) for k, v in test_results[1].items()))
