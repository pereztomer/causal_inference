import numpy as np
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.static import teams
import pandas as pd
import matplotlib.pyplot as plt
from nba_api.stats.static import teams

nba_teams = teams.get_teams()
# minisota = [team for team in nba_teams if team['abbreviation'] == 'MIN'][0]
# minisota_id = minisota['id']





for team_id in [team['id'] for team in nba_teams]:
    gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id,
                                                   date_from_nullable='1/1/1989',
                                                   date_to_nullable='1/7/2000')
    games = gamefinder.get_data_frames()[0]
    print('team: ', [team for team in nba_teams if team['id'] == team_id][0],
          'mean: ', np.mean(games['FG3A']), 'median: ', np.median(games['FG3A']))
# sns.histplot(data=games[games['WL'] == 'W'], x='FG3A', label='W')
# sns.histplot(data=games[games['WL'] == 'L'], x='FG3A', label='L')
# plt.legend()
# plt.show()
#

