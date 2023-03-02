from causalgraphicalmodels import CausalGraphicalModel


def generate_graph():
    sprinkler = CausalGraphicalModel(
        nodes=["Season",
               "Player X is on team A",
               "Player X is on team B",
               'Player X complete stats',
               "Player X is in the game",
               "Team A statistics of the season until the game"
               "Team B statistics of the season until the game"
               "Playoff game"
               "Player X is in the game for team A",
               "Player X is in the game for team B",
               "Team A statistics from game until scoring run",
               "Team B statistics from game until scoring run",
               "Home/Road game",
               "T - timeout after a scoring streak",
               "Y - scoring streak has stopped"],
        edges=[
            ("Season", "Player X is on team A"),
            ("Season", "Player X is on team B"),
            ("Season", "Player X complete stats"),
            ("Player X is on team A", "Team A statistics of the season until the game"),
            ("Player X complete stats", "Team A statistics of the season until the game"),
            ("Player X is on team B", "Team B statistics of the season until the game"),
            ("Player X complete stats", "Team B statistics of the season until the game"),
            ("Playoff game", "Player X is in the game for team A"),
            ("Playoff game", "Player X is in the game for team B"),
            ("Player X is in the game for team A", "Team A statistics from game until scoring run"),
            ("Player X is in the game for team B", "Team B statistics from game until scoring run"),
            ("Team A statistics of the season until the game", "Team A statistics from game until scoring run"),
            ("Team B statistics of the season until the game", "Team B statistics from game until scoring run"),
            ("Team A statistics from game until scoring run", "T - timeout after a scoring streak"),
            ("Team B statistics from game until scoring run", "T - timeout after a scoring streak"),
            ("T - timeout after a scoring streak", "Y - scoring streak has stopped")

        ]
    )

    observed_vars = ["Season",
                     "Team A statistics of the season until the game"
                     "Team B statistics of the season until the game"
                     "Playoff game",
                     "Team A statistics from game until scoring run",
                     "Team B statistics from game until scoring run",
                     "Home/Road game",
                     ]
    # draw return a graphviz `dot` object, which jupyter can render
    print(f'Backdoor criterion:'
          f' {sprinkler.is_valid_backdoor_adjustment_set("T - timeout after a scoring streak", "Y - scoring streak has stopped", set(observed_vars))}')

def main():
    generate_graph()


if __name__ == '__main__':
    main()
