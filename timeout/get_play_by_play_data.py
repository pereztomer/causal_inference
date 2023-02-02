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

from nba_api.stats.endpoints import playbyplay
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd


def check_if_diff_inc(df, ts, init_diff, period, home_run):
    if home_run == 1:  # means that diff should be positive
        max_diff = df[(df['PERIOD'] == period) & (df['PCTIMESTRING'] < ts) &
                      (df['PCTIMESTRING'] > ts - pd.Timedelta(minutes=2))]['diff'].max()

        if max_diff - init_diff < 4:
            return 0
        return 1
    elif home_run == 0:  # means that diff should be negative
        min_diff = df[(df['PERIOD'] == period) & (df['PCTIMESTRING'] < ts) &
                      (df['PCTIMESTRING'] > ts - pd.Timedelta(minutes=2))]['diff'].min()

        if min_diff - init_diff > -4:
            return 0
        return 1


def check_if_strike(df, ts, period, indicators):
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


def get_play_by_play_ds(season, path_to_save):
    game_finder = leaguegamefinder.LeagueGameFinder(season_nullable=season)
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
    final_ds = {'GAME_ID': [], 'TS': [], 'T': [], 'Y': [], 'home_run': [], 'SCORE_A': [], 'SCORE_B': [],
                'g_made_home': [], 'g_made_road': [], 'g_missed_home': [], 'g_missed_road': [],
                'fta_home': [], 'fta_road': [], 'rebound_home': [], 'rebound_road': [],
                'to_home': [], 'to_road': []
                }

    for game_id in games_df['GAME_ID'].unique():

        # Query for the play by play of that most recent regular season game
        try:
            df = playbyplay.PlayByPlay(game_id).get_data_frames()[0]
        except:
            continue

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

                if init_diff >= 8 or init_diff <= -8:
                    home_run = 1 if init_diff >= 8 else 0

                    index_to_remove += list(sus_index)
                    y = check_if_diff_inc(df, row['PCTIMESTRING'], init_diff, row['PERIOD'], home_run)
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
                    final_ds['home_run'].append(home_run)

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
            if (7 <= init_diff <= 9) or (-9 <= init_diff <= -7):
                home_run = 1 if init_diff >= 0 else 0

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
                final_ds['home_run'].append(home_run)

        game_count += 1

        if game_count % 100 == 0:
            print(f"Done with game {game_count} out of {len(games_df['GAME_ID'].unique())}")

    final_ds = pd.DataFrame(final_ds)
    final_ds.to_csv(path_to_save)
