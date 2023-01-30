from nba_api.stats.static import teams
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np


def combine_team_games(df, keep_method='home'):
    '''Combine a TEAM_ID-GAME_ID unique table into rows by game. Slow.

        Parameters
        ----------
        df : Input DataFrame.
        keep_method : {'home', 'away', 'winner', 'loser', ``None``}, default 'home'
            - 'home' : Keep rows where TEAM_A is the home team.
            - 'away' : Keep rows where TEAM_A is the away team.
            - 'winner' : Keep rows where TEAM_A is the losing team.
            - 'loser' : Keep rows where TEAM_A is the winning team.
            - ``None`` : Keep all rows. Will result in an output DataFrame the same
                length as the input DataFrame.

        Returns
        -------
        result : DataFrame
    '''
    # Join every row to all others with the same game ID.
    joined = pd.merge(df, df, suffixes=['_A', '_B'],
                      on=['SEASON_ID', 'GAME_ID', 'GAME_DATE'])
    # Filter out any row that is joined to itself.
    result = joined[joined.TEAM_ID_A != joined.TEAM_ID_B]
    # Take action based on the keep_method flag.
    if keep_method is None:
        # Return all the rows.
        pass
    elif keep_method.lower() == 'home':
        # Keep rows where TEAM_A is the home team.
        result = result[result.MATCHUP_A.str.contains(' vs. ')]
    elif keep_method.lower() == 'away':
        # Keep rows where TEAM_A is the away team.
        result = result[result.MATCHUP_A.str.contains(' @ ')]
    elif keep_method.lower() == 'winner':
        result = result[result.WL_A == 'W']
    elif keep_method.lower() == 'loser':
        result = result[result.WL_A == 'L']
    else:
        raise ValueError(f'Invalid keep_method: {keep_method}')
    return result


def main():
    nba_teams = teams.get_teams()
    teams_id = [val['id'] for val in nba_teams]
    games = pd.DataFrame()
    for t_id in teams_id:
        df = leaguegamefinder.LeagueGameFinder(team_id_nullable=t_id).get_data_frames()[0]
        games = pd.concat([games, df])

    games = combine_team_games(games)
    games = games.reset_index()
    games = games.drop(['index'], axis=1)
    games.to_csv('data/games.csv')

    # season_id_date_mapping = games[['SEASON_ID', 'GAME_DATE']]
    # season_id_date_mapping_dict = {}
    # for index, row in season_id_date_mapping.iterrows():
    #     if row['SEASON_ID'] in season_id_date_mapping_dict:
    #         season_id_date_mapping_dict[row['SEASON_ID']].append(row['GAME_DATE'])
    #     else:
    #         season_id_date_mapping_dict[row['SEASON_ID']] = [row['GAME_DATE']]



def combine_ds():
    total_games = pd.read_csv('./data/games.csv')
    print('hi')

if __name__ == '__main__':
    combine_ds()
