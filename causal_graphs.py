from causalnex.structure import StructureModel
import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms.dag import descendants
from networkx.algorithms.dag import ancestors


def main():

    # # Create an empty graph
    # G = nx.DiGraph()
    #
    # # Add nodes to the graph
    # G.add_node('Smoking')
    # G.add_node('Cancer')
    # G.add_node('Tar')
    # G.add_node('Nicotine')
    #
    # # Add edges to the graph
    # G.add_edge('Smoking', 'Cancer')
    # G.add_edge('Tar', 'Cancer')
    # G.add_edge('Nicotine', 'Cancer')
    # G.add_edge('Nicotine', 'Smoking')
    #
    # # Draw the graph
    # nx.draw(G, with_labels=True)
    # plt.show()
    #
    #
    # # Create a structure model
    # sm = StructureModel(G)

    # Create a structure model - different way
    # sm_manual = StructureModel()
    # sm_manual.add_edges_from(
    #     [
    #         ("b", "a"),
    #         ("b", "c"),
    #         ("d", "a"),
    #         ("d", "c"),
    #         ("d", "b"),
    #         ("e", "c"),
    #         ("e", "b"),
    #     ],
    #     origin="expert",
    # )
    # Let's say the treatment variable is 'A' and the outcome variable is 'E'.
    G = nx.DiGraph()
    G.add_edges_from([('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'E')])
    nx.draw(G, with_labels=True)
    plt.show()


    # https://towardsdatascience.com/causal-kung-fu-in-python-3-basic-techniques-to-jump-start-your-causal-inference-journey-tonight-ae09181704f7
    backdoor = ancestors(G, 'E') - {'A'}
    print(f'backdoor: {backdoor}')
    frontdoor = descendants(G, 'A') & ancestors(G, 'E')
    print(f'frontdoor: {frontdoor}')


if __name__ == '__main__':
    main()