# class EventMsgType(Enum):
#     FIELD_GOAL_MADE = 1
#     FIELD_GOAL_MISSED = 2
#     FREE_THROWfree_throw_attempt = 3
#     REBOUND = 4
#     TURNOVER = 5
#     FOUL = 6
#     VIOLATION = 7
#     SUBSTITUTION = 8
#     TIMEOUT = 9
#     JUMP_BALL = 10
#     EJECTION = 11
#     PERIOD_BEGIN = 12
#     PERIOD_END = 13

# print(f'Searching through {len(games)} game(s) for the game_id of {game_id} where {game_matchup}')
#
#         # Query for the play by play of that most recent regular season game
#         df = playbyplay.PlayByPlay(game_id).get_data_frames()[0]
#         print(df.head())  # just looking at the head of the data
#         df.to_csv(f'data/play_by_play/{game_id}.csv')
import numpy as np
from nba_api.stats.endpoints import playbyplay
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.library.parameters import Season
import pandas as pd
from nba_api.stats.library.parameters import SeasonType


def find_strikes(df, team, opp):
    row_index = 0
    curr_team_score = 0
    curr_opp_score = 0
    strikes = []
    curr_strike = []
    for index, row in df.iterrows():
        if row[team] == -1 or row[team] == 0:
            continue

        if row[team] > curr_team_score:
            curr_strike.append(row['EVENTNUM'])
            curr_team_score = row[team]
        else:
            if len(curr_strike) >= 8:
                strikes.append(curr_strike)
            curr_strike = []
            curr_team_score = 0
    return strikes
    #     if row[team] > 0:
    #         row_index = index
    #         curr_team_score = row[team]
    #         curr_opp_score = row[opp]
    #         break
    #
    # df[df[team] > curr_team_score]


def check_if_diff_inc(df, ts, init_diff, period, pdt=2):
    max_diff = df[(df['PERIOD'] == period) & (df['PCTIMESTRING'] < ts) &
                  (df['PCTIMESTRING'] > ts - pd.Timedelta(minutes=2))]['diff'].max()

    if max_diff - init_diff < 4:
        return 0
    return 1


def check_if_strike(df, ts, period, indicators, pdt=2):
    diff_df = df[(df['PERIOD'] == period) & (df['PCTIMESTRING'] > ts) &
                 (df['PCTIMESTRING'] < ts + pd.Timedelta(minutes=2))]
    diff_df = diff_df.drop(indicators, errors='ignore')
    copy_diff_df = diff_df['diff'].copy()
    copy_diff_df = copy_diff_df.dropna()
    copy_diff_df = copy_diff_df.astype({'diff': 'int32'})

    if len(copy_diff_df) == 0:
        return 0, []

    if copy_diff_df.idxmax() < copy_diff_df.idxmin():

        init_diff = diff_df['diff'].min() - diff_df['diff'].max()
    else:
        init_diff = diff_df['diff'].max() - diff_df['diff'].min()

    return init_diff, diff_df.index


def main():
    game_finder = leaguegamefinder.LeagueGameFinder(season_nullable='2018-19')

    games_df = game_finder.get_data_frames()[0]

    games_df['Playyoff Game'] = games_df['SEASON_ID'].apply(
        lambda x: 1 if (int(str(x)[0]) == 4 or int(str(x)[0]) == 5) else 0)
    games_df['Regular Season Game'] = games_df['SEASON_ID'].apply(
        lambda x: 1 if int(str(x)[0]) == 2 else 0)

    games_df = games_df[(games_df['Playyoff Game'] == 1) | (games_df['Regular Season Game'] == 1)]

    nba_teams = teams.get_teams()
    teams_id = [val['id'] for val in nba_teams]
    games_df.loc[:, 'TEAM_ID'] = games_df['TEAM_ID'].apply(lambda x: x if x in teams_id else -1)
    games_df = games_df[games_df['TEAM_ID'] != -1]

    game_count = 0
    final_ds = {'GAME_ID': [], 'TS': [], 'T': [], 'Y': [], 'SCORE_A': [], 'SCORE_B': [],
                'g_made_home': [], 'g_made_road': [], 'g_missed_home': [], 'g_missed_road': [],
                'fta_home': [], 'fta_road': [], 'rebound_home': [], 'rebound_road': [],
                'to_home': [], 'to_road': []
                }

    for game_id in games_df['GAME_ID'].unique():

        # print('Game ID :', game_id)

        # Query for the play by play of that most recent regular season game
        try:
            df = playbyplay.PlayByPlay(game_id).get_data_frames()[0]
        except:
            continue

        # df = df[(df['EVENTMSGTYPE'] == 3) | (df['EVENTMSGTYPE'] == 1) | (df['EVENTMSGTYPE'] == 9)]

        df.loc[:, 'diff'] = df['SCORE'].apply(lambda x: int(x.split('-')[1]) -
                                                        int(x.split('-')[0]) if x is not None else pd.NA)
        df.loc[:, 'PCTIMESTRING'] = pd.to_datetime(df['PCTIMESTRING'], format='%M:%S')

        stats = {'g_made_home': 0, 'g_made_road': 0, 'g_missed_home': 0, 'g_missed_road': 0,
                 'fta_home': 0, 'fta_road': 0, 'rebound_home': 0, 'rebound_road': 0,
                 'to_home': 0, 'to_road': 0}
        index_to_remove = []
        curr_a_score = 0
        curr_b_score = 0
        for index, row in df.iterrows():

            if row['EVENTMSGTYPE'] == 1:
                if row['HOMEDESCRIPTION'] is not None:
                    stats['g_made_home'] += 1
                else:
                    stats['g_made_road'] += 1

            if row['EVENTMSGTYPE'] == 2:
                if row['HOMEDESCRIPTION'] is not None:
                    stats['g_missed_home'] += 1
                else:
                    stats['g_missed_road'] += 1

            if row['EVENTMSGTYPE'] == 3:
                if row['HOMEDESCRIPTION'] is not None:
                    stats['fta_home'] += 1
                else:
                    stats['fta_road'] += 1

            if row['EVENTMSGTYPE'] == 4:
                if row['HOMEDESCRIPTION'] is not None:
                    stats['rebound_home'] += 1
                else:
                    stats['rebound_road'] += 1

            if row['EVENTMSGTYPE'] == 5:
                if row['HOMEDESCRIPTION'] is not None:
                    stats['to_home'] += 1
                else:
                    stats['to_road'] += 1

            if row['SCORE'] is not None:
                curr_a_score = row['SCORE'].split('-')[1]
                curr_b_score = row['SCORE'].split('-')[0]

            if row['EVENTMSGTYPE'] == 9:
                init_diff, sus_index = check_if_strike(df, row['PCTIMESTRING'], row['PERIOD'], [])

                if init_diff >= 8:
                    index_to_remove += list(sus_index)
                    y = check_if_diff_inc(df, row['PCTIMESTRING'], init_diff, row['PERIOD'])
                    final_ds['GAME_ID'].append(row['GAME_ID'])
                    final_ds['T'].append(1)
                    final_ds['Y'].append(y)
                    final_ds['TS'].append(row['PCTIMESTRING'])
                    final_ds['SCORE_A'].append(curr_a_score)
                    final_ds['SCORE_B'].append(curr_b_score)
                    final_ds['g_made_home'].append(stats['g_made_home'])
                    final_ds['g_made_road'].append(stats['g_made_road'])
                    final_ds['g_missed_home'].append(stats['g_missed_home'])
                    final_ds['g_missed_road'].append(stats['g_missed_road'])
                    final_ds['fta_home'].append(stats['fta_home'])
                    final_ds['fta_road'].append(stats['fta_road'])
                    final_ds['rebound_home'].append(stats['rebound_home'])
                    final_ds['rebound_road'].append(stats['rebound_road'])
                    final_ds['to_home'].append(stats['to_home'])
                    final_ds['to_road'].append(stats['to_road'])

        df = df.drop(index_to_remove)

        indicators = []

        curr_a_score = 0
        curr_b_score = 0
        stats = {'g_made_home': 0, 'g_made_road': 0, 'g_missed_home': 0, 'g_missed_road': 0,
                 'fta_home': 0, 'fta_road': 0, 'rebound_home': 0, 'rebound_road': 0,
                 'to_home': 0, 'to_road': 0}
        for index, row in df.iterrows():
            if row['EVENTMSGTYPE'] == 1:
                if row['HOMEDESCRIPTION'] is not None:
                    stats['g_made_home'] += 1
                else:
                    stats['g_made_road'] += 1

            if row['EVENTMSGTYPE'] == 2:
                if row['HOMEDESCRIPTION'] is not None:
                    stats['g_missed_home'] += 1
                else:
                    stats['g_missed_road'] += 1

            if row['EVENTMSGTYPE'] == 3:
                if row['HOMEDESCRIPTION'] is not None:
                    stats['fta_home'] += 1
                else:
                    stats['fta_road'] += 1

            if row['EVENTMSGTYPE'] == 4:
                if row['HOMEDESCRIPTION'] is not None:
                    stats['rebound_home'] += 1
                else:
                    stats['rebound_road'] += 1

            if row['EVENTMSGTYPE'] == 5:
                if row['HOMEDESCRIPTION'] is not None:
                    stats['to_home'] += 1
                else:
                    stats['to_road'] += 1

            if row['SCORE'] is not None:
                curr_a_score = row['SCORE'].split('-')[1]
                curr_b_score = row['SCORE'].split('-')[0]

            init_diff, index_indicate = check_if_strike(df, row['PCTIMESTRING'], row['PERIOD'], indicators)
            if init_diff == 8:
                indicators += list(index_indicate)
                y = check_if_diff_inc(df, row['PCTIMESTRING'], init_diff, row['PERIOD'])
                final_ds['GAME_ID'].append(row['GAME_ID'])
                final_ds['T'].append(0)
                final_ds['Y'].append(y)
                final_ds['TS'].append(row['PCTIMESTRING'])
                final_ds['SCORE_A'].append(curr_a_score)
                final_ds['SCORE_B'].append(curr_b_score)
                final_ds['g_made_home'].append(stats['g_made_home'])
                final_ds['g_made_road'].append(stats['g_made_road'])
                final_ds['g_missed_home'].append(stats['g_missed_home'])
                final_ds['g_missed_road'].append(stats['g_missed_road'])
                final_ds['fta_home'].append(stats['fta_home'])
                final_ds['fta_road'].append(stats['fta_road'])
                final_ds['rebound_home'].append(stats['rebound_home'])
                final_ds['rebound_road'].append(stats['rebound_road'])
                final_ds['to_home'].append(stats['to_home'])
                final_ds['to_road'].append(stats['to_road'])
        game_count += 1



        if game_count % 20 == 0:
            print(f"Done with game {game_count} out of {len(games_df['GAME_ID'])}")

    final_ds = pd.DataFrame(final_ds)
    final_ds.to_csv('data\Timeout.csv')


if __name__ == '__main__':
    main()
