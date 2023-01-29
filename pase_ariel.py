from nba_api.stats.endpoints import boxscoreadvancedv2
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
import numpy as np


def get_pace_by_game_id_and_team_id(game_id, team_id):
    out = boxscoreadvancedv2.BoxScoreAdvancedV2(game_id=game_id)

    teams_id_2 = out.team_stats.data['data'][1][1]
    location = 0
    if teams_id_2 == team_id:
        location = 1
    pace = out.team_stats.data['data'][location][25]

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
        season_game_id_df.loc[:, "PACE"] = np.nan
        for index, s_g in season_game_id_df.iterrows():
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
            if index == 5:
                break
        print('hi')


def main():
    out = boxscoreadvancedv2.BoxScoreAdvancedV2(game_id='0022200742')
    print(out)
    pace_1 = out.team_stats.data['data'][0][25]
    pace_2 = out.team_stats.data['data'][1][25]


if __name__ == '__main__':
    generate_ds_pace()
