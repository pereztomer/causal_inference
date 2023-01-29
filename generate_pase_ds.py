from nba_api.stats.endpoints import boxscoreadvancedv2
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
import numpy as np
import os
import pandas as pd


def generate_ds_pace():
    nba_teams = teams.get_teams()
    all_teams_id = [val['id'] for val in nba_teams]
    for team_id in all_teams_id:
        # Query for games where the Celtics were playing
        gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id,
                                                       date_from_nullable='1/1/2010',
                                                       date_to_nullable='1/7/2020')
        # The first DataFrame of those returned is what we want.
        team_games = gamefinder.get_data_frames()[0]
        season_game_id_df = team_games[['SEASON_ID', 'GAME_ID', 'TEAM_NAME', 'TEAM_ID']]
        season_game_id_df.loc[season_game_id_df.index, "PACE"] = np.nan
        for index, s_g in season_game_id_df.iterrows():
            if index == 0:
                os.makedirs(f'pace_csv/{s_g["TEAM_ID"]}', exist_ok=True)
            out = boxscoreadvancedv2.BoxScoreAdvancedV2(game_id=s_g['GAME_ID'])

            teams_id_1 = out.team_stats.data['data'][0][1]
            teams_id_2 = out.team_stats.data['data'][1][1]
            if teams_id_1 == s_g['TEAM_ID']:
                location = 0
            elif teams_id_2 == s_g['TEAM_ID']:
                location = 1
            else:
                print('ERROR!')
            pace = out.team_stats.data['data'][location][25]
            season_game_id_df.loc[season_game_id_df["GAME_ID"] == s_g['GAME_ID'], 'PACE'] = pace
            if index % 10 == 0:
                season_game_id_df.to_csv(f'pace_csv/{s_g["TEAM_ID"]}/{index}_file_test.csv')

        season_game_id_df.to_csv(f'pace_csv/{s_g["TEAM_ID"]}/final_file_test.csv')
        print('hi')


if __name__ == '__main__':
    out = pd.read_csv('/home/tomer/PycharmProjects/causal_inference/pace_csv/2022-2023.csv',
                      encoding='utf-8',
                      header=6)
    # generate_ds_pace()
    print('hi')
