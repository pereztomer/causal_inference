from nba_api.stats.static import teams
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from datetime import datetime
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


def moving_avg(df, team_id, date, feature, n=10):
    curr_df = df[['TEAM_ID_A', 'GAME_DATE', 'SEASON', 'Playyoff Game'] + [feature]].copy()
    curr_val = curr_df[(curr_df['GAME_DATE'] == date) & (curr_df['TEAM_ID_A'] == team_id)]

    curr_season = int(curr_val['SEASON'])

    curr_playoff = int(curr_val['Playyoff Game'])
    dates_df = curr_df[(curr_df['GAME_DATE'] < date) & (curr_df['TEAM_ID_A'] == team_id) &
                       (curr_df['SEASON'] == curr_season) & (curr_df['Playyoff Game'] == curr_playoff)]
    dates_df = dates_df.sort_values("GAME_DATE", ascending=False).reset_index()

    if len(dates_df) == 0:
        return None
    elif len(dates_df) < n:
        return dates_df[feature].mean()
    return dates_df.iloc[range(n)][feature].mean()


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

    result = result[result['YEAR_A'] >= 1996]

    result = result[['TEAM_ID_A', 'TEAM_A', 'GAME_ID', 'GAME_DATE', 'WL_A', 'FG3A_A',
                     'TEAM_ID_B', 'TEAM_B', 'YEAR_A', 'Playyoff Game', 'Regular Season Game',
                     'Preseason Game', 'All-star Game', 'GP_A', 'W_A', 'OFFRTG_A', 'DEFRTG_A',
                     'NETRTG_A', 'AST%_A', 'AST/TO_A', 'AST RATIO_A', 'OREB%_A', 'DREB%_A', 'REB%_A',
                     'TOV%_A', 'EFG%_A', 'TS%_A', 'PACE_A', 'GP_B', 'W_B', 'OFFRTG_B', 'DEFRTG_B',
                     'NETRTG_B', 'AST%_B', 'AST/TO_B', 'AST RATIO_B', 'OREB%_B', 'DREB%_B', 'REB%_B',
                     'TOV%_B', 'EFG%_B', 'TS%_B', 'PACE_B']]
    result = result.dropna().drop_duplicates()

    result.loc[:, 'GAME_DATE'] = pd.to_datetime(result['GAME_DATE'])
    result = result[(result['Preseason Game'] != 1) & (result['All-star Game'] != 1)]
    result = result.rename(columns={'YEAR_A': 'SEASON', 'FG3A_A': 'FG3A_FOR_GAME', 'WL_A': 'WL'})
    result.loc[:, 'WP_A'] = result.apply(lambda row: row['W_A'] / row['GP_A'], axis=1)
    result.drop(columns=['W_A', 'GP_A'])
    result.loc[:, 'WP_B'] = result.apply(lambda row: row['W_B'] / row['GP_B'], axis=1)
    result.drop(columns=['W_B', 'GP_B'])

    mirror_df = result.copy()
    a_cols = [col for col in mirror_df.columns if '_A' in col]
    b_cols = [col for col in mirror_df.columns if '_B' in col]

    mirror_df[a_cols + b_cols] = mirror_df[b_cols + a_cols]

    result.loc[:, 'home_game'] = 1
    mirror_df.loc[:, 'home_game'] = 0

    result = pd.concat([result, mirror_df])

    result.loc[:, 'T'] = result.apply(lambda x: moving_avg(result, x['TEAM_ID_A'],
                                                           x['GAME_DATE'], 'FG3A_FOR_GAME'), axis=1)

    result.to_csv('data\\final_ds.csv')


def add_binary_treatment(df):
    nba_teams = teams.get_teams()
    teams_id = [val['id'] for val in nba_teams]

    seasons = df['SEASON'].unique()
    playoff_values = [0, 1]

    for team_id in teams_id:
        for season in seasons:
            for playoff in playoff_values:
                mask = (df['TEAM_ID_A'] == team_id) & (df['SEASON'] == season) & (df['Playyoff Game'] == playoff)
                norm_term = df[mask]['T'].mean()
                df.loc[mask, 'T'] = df[mask]['T'].apply(lambda x: x/norm_term)
                df.loc[mask, 'T'] = df[mask]['T'].apply(lambda x: 0 if x < 1 else 1)

    df.to_csv('final_ds_with_normalized_t.csv')

if __name__ == '__main__':
    # combine_ds()
    final_df = pd.read_csv('data\\final_ds.csv')
    add_binary_treatment(final_df)
