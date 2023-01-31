import datetime

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


def normalize_time(x):
    out = x['PCTIMESTRING'] + datetime.timedelta(minutes=12) * (x['PERIOD']-1)
    return out


def main():
    game_finder = leaguegamefinder.LeagueGameFinder(season_nullable='2018-19')

    games_dict = game_finder.get_normalized_dict()
    games = games_dict['LeagueGameFinderResults']
    for game in games:
        game_id = game['GAME_ID']
        game_match_up = game['MATCHUP']
        # print('Game ID :', game_id)

        # Query for the play by play of that most recent regular season game
        df = playbyplay.PlayByPlay(game_id).get_data_frames()[0]
        df = df[['EVENTNUM', 'PCTIMESTRING', 'PERIOD', 'EVENTMSGTYPE', 'SCORE']]

        df = df[(df['EVENTMSGTYPE'] == 3) | (df['EVENTMSGTYPE'] == 1) | (df['EVENTMSGTYPE'] == 9)]

        df.loc[:, 'diff'] = df['SCORE'].apply(lambda x: int(x.split('-')[0]) -
                                                        int(x.split('-')[1]) if x is not None else -1)

        df.loc[:, 'PCTIMESTRING'] = pd.to_datetime(df['PCTIMESTRING'], format='%M:%S')
        df['game_time'] = df.apply(lambda x: normalize_time(x), axis=1)
        df = df.drop(['PCTIMESTRING'], axis=1).sort_values(['game_time'])
        time_stamps = df[df['EVENTMSGTYPE'] == 9].copy()

        prev = 0
        # for index, row in df.iterrows():
        #     if row['EVENTMSGTYPE'] == 9:
        #         while df.iloc[prev]['PCTIMESTRING'] > 2:
        #             prev += 1
        #
        #         for i in range(prev, index):
        #             if df.iloc[i]['diff'] > 8:
        #                 curr_index = index
        #                 while df.iloc[curr_index]['PCTIMESTRING'] - row['EVENTMSGTYPE']['PCTIMESTRING'] > 2:
        #
        #
        #                 final_ds.append((row['EVENTNUM'], 1, ))
        #
        #
        #
        #
        # timeout_df = df[df['EVENTMSGTYPE'] == 9]['EVENTNUM', 'PCTIMESTRING', 'diff']
        #
        #
        #
        #
        # df.loc[df['EVENTMSGTYPE'] == 9, '2MS'] = df[df['EVENTMSGTYPE'] == 9].apply(lambda row: row[])
        # # df.loc[:, 'HOME_SCORE'] = df['SCORE'].apply(lambda x: int(x.split('-')[0]) if x is not None else -1)
        # # df.loc[:, 'GUST_SCORE'] = df['SCORE'].apply(lambda x: int(x.split('-')[1]) if x is not None else -1)
        # #
        # # strikes = find_strikes(df, 'HOME_SCORE', '')


if __name__ == '__main__':
    main()
