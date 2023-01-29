from nba_api.stats.static import teams
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np


def main():
    nba_teams = teams.get_teams()
    teams_id = [val['id'] for val in nba_teams]
    games = pd.DataFrame()
    for t_id in teams_id:
        df = leaguegamefinder.LeagueGameFinder(team_id_nullable=t_id).get_data_frames()[0]
        games = pd.concat([games, df])

    games.to_csv('data/games.csv')


if __name__ == '__main__':
    main()
