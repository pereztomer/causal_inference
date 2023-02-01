from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.static import teams


def moving_avg(df, x):

    relevant_features = ['TEAM_NAME', 'TEAM_ID', 'GAME_ID', 'GAME_DATE', 'MATCHUP',
                         'WL', 'MIN',
                         'PTS', 'FGM', 'FGA', 'FG_PCT',
                         'FG3M', 'FG3A', 'FG3_PCT', 'FTM',
                         'FTA', 'FT_PCT', 'OREB', 'DREB',
                         'REB', 'AST', 'STL', 'BLK', 'TOV',
                         'PF', 'PLUS_MINUS', 'Playyoff Game',
                         'Regular Season Game']
    curr_df = df[relevant_features].copy()

    dates_df = curr_df[(curr_df['GAME_DATE'] < x['GAME_DATE']) &
                       (curr_df['TEAM_ID'] == x['TEAM_ID']) &
                       (curr_df['Playyoff Game'] == x['Playyoff Game'])]

    avg_df = dates_df[['PTS', 'FGM', 'FGA', 'FG_PCT',
                       'FG3M', 'FG3A', 'FG3_PCT', 'FTM',
                       'FTA', 'FT_PCT', 'OREB', 'DREB',
                       'REB', 'AST', 'STL', 'BLK', 'TOV',
                       'PF', 'PLUS_MINUS']]
    avg_df = avg_df.mean()
    x['avg_PTS'] = avg_df['PTS']
    x['avg_FGM'] = avg_df['FGM']
    x['avg_FGA'] = avg_df['FGA']
    x['avg_FG_PCT'] = avg_df['FG_PCT']
    x['avg_FG3M'] = avg_df['FG3M']
    x['avg_FG3A'] = avg_df['FG3A']
    x['avg_FG3_PCT'] = avg_df['FG3_PCT']
    x['avg_FTM'] = avg_df['FTM']
    x['avg_FTA'] = avg_df['FTA']
    x['avg_FT_PCT'] = avg_df['FT_PCT']
    x['avg_OREB'] = avg_df['OREB']
    x['avg_DREB'] = avg_df['DREB']
    x['avg_REB'] = avg_df['REB']
    x['avg_AST'] = avg_df['AST']
    x['avg_STL'] = avg_df['STL']
    x['avg_BLK'] = avg_df['BLK']
    x['avg_TOV'] = avg_df['TOV']
    x['avg_PF'] = avg_df['PF']
    x['avg_PLUS_MINUS'] = avg_df['PLUS_MINUS']

    return x


def create_ds_till_game(season, path_to_save):
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

    games_df = games_df.apply(lambda x: moving_avg(games_df, x), axis=1)
    games_df.to_csv(path_to_save)

