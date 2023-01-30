from nba_api.stats.static import teams
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from glob import glob


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


def collect_pace():
    files = glob('data\\pace_csv\\*.csv', recursive=True)
    total_pace_df = pd.DataFrame()
    for file in files:
        df = pd.read_csv(file)
        df.loc[:, 'YEAR'] = int(file.split('\\')[-1].split('_')[1])
        total_pace_df = pd.concat([total_pace_df, df])

    return total_pace_df


def get_treatment(team_id, date):
    pass


def combine_ds():
    total_games = pd.read_csv('./data/games.csv')
    total_games = total_games.drop(columns=['index'], axis=1)
    total_games = total_games.rename(columns={'TEAM_NAME_A': 'TEAM_A', 'TEAM_NAME_B': 'TEAM_B'})
    total_games['YEAR_A'] = total_games['SEASON_ID'].apply(lambda x: int(str(x)[1:]))
    total_games['YEAR_B'] = total_games['SEASON_ID'].apply(lambda x: int(str(x)[1:]))
    total_games['Playyoff Game'] = total_games['SEASON_ID'].apply(
        lambda x: 1 if (int(str(x)[0]) == 4 or int(str(x)[0]) == 5) else 0)
    total_games['Regular Season Game'] = total_games['SEASON_ID'].apply(
        lambda x: 1 if int(str(x)[0]) == 2 else 0)
    total_games['Preseason Game'] = total_games['SEASON_ID'].apply(
        lambda x: 1 if int(str(x)[0]) == 1 else 0)
    total_games['All-star Game'] = total_games['SEASON_ID'].apply(
        lambda x: 1 if int(str(x)[0]) == 3 else 0)
    total_pace_df = collect_pace()
    total_pace_df_A = total_pace_df.add_suffix('_A')
    total_pace_df_B = total_pace_df.add_suffix('_B')
    result = pd.merge(total_games, total_pace_df_A, how='left', on=['TEAM_A', 'YEAR_A'])
    result = pd.merge(result, total_pace_df_B, how='left', on=['TEAM_B', 'YEAR_B'])

    result = result[['TEAM_A_ID', 'TEAM_A', 'GAME_ID', 'GAME_DATE', 'WL_A', 'FG3A_A',
                     'TEAM_ID_B', 'TEAM_B', 'YEAR_A', 'PlayyoffGame', 'Regular Season Game'
                     'Pre Season Game', 'All-star Game', 'GP_A', 'W_A', 'OFFRTG_A', 'DEFRTG_A',
                     'NETRTG_A', 'AST%_A', 'AST/TO_A', 'AST RATIO_A', 'OREB%_A', 'DREB%_A', 'REB%_A',
                     'TOV%_A', 'EFG%_A', 'TS%_A', 'PACE_A', 'GP_B', 'W_B', 'OFFRTG_B', 'DEFRTG_B',
                     'NETRTG_B', 'AST%_B', 'AST/TO_B', 'AST RATIO_B', 'OREB%_B', 'DREB%_B', 'REB%_B',
                     'TOV%_B', 'EFG%_B', 'TS%_B', 'PACE_B',]]


if __name__ == '__main__':
    combine_ds()
