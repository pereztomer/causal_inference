from nba_api.stats.endpoints import playbyplay
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.library.parameters import Season
from nba_api.stats.library.parameters import SeasonType


def main():
    nba_teams = teams.get_teams()

    # Select the dictionary for the Pacers, which contains their team ID
    pacers = [team for team in nba_teams if team['abbreviation'] == 'IND'][0]
    pacers_id = pacers['id']
    print(f'pacers_id: {pacers_id}')

    gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable=Season.default)

    games_dict = gamefinder.get_normalized_dict()
    games = games_dict['LeagueGameFinderResults']
    for game in games:
        game_id = game['GAME_ID']
        game_matchup = game['MATCHUP']

        print(f'Searching through {len(games)} game(s) for the game_id of {game_id} where {game_matchup}')

        # Query for the play by play of that most recent regular season game
        df = playbyplay.PlayByPlay(game_id).get_data_frames()[0]
        print(df.head())  # just looking at the head of the data
        df.to_csv(f'data/play_by_play/{game_id}.csv')
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


if __name__ == '__main__':
    main()
