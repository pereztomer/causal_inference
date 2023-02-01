import pandas as pd
from get_play_by_play_data import get_play_by_play_ds
from get_statistics_until_game import create_ds_till_game
import os

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


def combine_play_by_play_stats(p_path, stats_path, save_path):
    general_stats_18 = pd.read_csv(stats_path)

    general_stats_18 = combine_team_games(general_stats_18)

    cols_to_take = [col for col in general_stats_18.columns if 'avg' in col]
    cols_to_take += ['GAME_ID', 'TEAM_ABBREVIATION_A', 'TEAM_ABBREVIATION_B']

    general_stats_18 = general_stats_18[cols_to_take]

    play_by_play_18 = pd.read_csv(p_path)
    play_by_play_18 = play_by_play_18.drop(columns=['Unnamed: 0', ])

    df_18 = play_by_play_18.join(general_stats_18.set_index('GAME_ID'), on='GAME_ID')
    df_18.to_csv(save_path)


def main():

    seasons_to_get = ['2018-19', '2019-20', '2020-21', '2021-22', '2022-23']
    path_to_save = 'data'

    for season in seasons_to_get:
        print(f'Starting with season {season}')
        os.makedirs(f'{path_to_save}\\{season}', exist_ok=True)
        play_by_play_path = f'{path_to_save}\\{season}\\{season}_play_by_play.csv'
        stats_path = f'{path_to_save}\\{season}\\{season}_general_stats_till_game.csv'
        final_path = f'{path_to_save}\\{season}\\{season}_timeout_final.csv'

        get_play_by_play_ds(season=season, path_to_save=play_by_play_path)
        create_ds_till_game(season=season, path_to_save=stats_path)
        combine_play_by_play_stats(p_path=play_by_play_path, stats_path=stats_path,
                                   save_path=final_path)


if __name__ == '__main__':
    main()