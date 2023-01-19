from nba_api.stats.static import teams
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder
import datetime
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

def three_point_over_the_years_graph():
    nba_teams = teams.get_teams()
    teams_id = [val['id'] for val in nba_teams]
    games = pd.DataFrame()
    for t_id in teams_id:
        df = leaguegamefinder.LeagueGameFinder(team_id_nullable=t_id).get_data_frames()[0]
        games = pd.concat([games, df])

    date_3pt = games[['GAME_DATE', 'FG3A']]
    date_3pt['YEAR'] = date_3pt['GAME_DATE'].apply(lambda x: int(x[:4]))
    date_3pt = date_3pt.drop('GAME_DATE', axis=1)
    three_p_avg_by_year = date_3pt.groupby('YEAR').mean()
    print(three_p_avg_by_year)

    # Assuming 'date_3pt' is your DataFrame
    mean_by_year = date_3pt.groupby('YEAR').mean()

    mean_by_year.plot(kind='bar')
    plt.xlabel('Year')
    plt.ylabel('Mean')
    plt.title('Mean by Year')
    plt.show()


def team_3_point_win_graph():
    nba_teams = teams.get_teams()
    teams_id = [val['id'] for val in nba_teams]
    games = pd.DataFrame()
    for t_id in teams_id:
        df = leaguegamefinder.LeagueGameFinder(team_id_nullable=t_id).get_data_frames()[0]
        games = pd.concat([games, df])

    compact = games[['GAME_DATE', 'TEAM_NAME', 'WL', 'FG3A']]
    compact['YEAR'] = compact['GAME_DATE'].apply(lambda x: int(x[:4]))
    compact = compact.drop('GAME_DATE', axis=1)
    compact = compact.loc[compact['YEAR'] > 2018]
    compact['numeric_wl'] = compact['WL'].apply(lambda x: 1 if x == 'W' else 0)
    compact = compact.drop('WL', axis=1)
    agg_df = compact.groupby('TEAM_NAME').agg({'numeric_wl': 'sum',
                                               'FG3A': 'mean'})

    team_colors = dict(zip(agg_df.index, mcolors.CSS4_COLORS.values()))

    # create a scatter plot
    plt.scatter(agg_df['numeric_wl'], agg_df['FG3A'], c=[team_colors[x] for x in agg_df.index])

    # add labels
    plt.xlabel('numeric_wl')
    plt.ylabel('FG3A')

    # add title
    plt.title('numeric_wl vs FG3A by team')

    coefs = np.polyfit(agg_df['numeric_wl'], agg_df['FG3A'], 1)

    plt.plot(agg_df['numeric_wl'], coefs[0] * agg_df['numeric_wl'] + coefs[1], color='red')

    # show plot
    plt.show()


if __name__ == '__main__':
    team_3_point_win_graph()
