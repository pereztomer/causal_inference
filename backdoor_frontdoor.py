from causalgraphicalmodels import CausalGraphicalModel
import matplotlib.pyplot as plt
import networkx as nx
def generate_graph():
    sprinkler = CausalGraphicalModel(
        nodes=["x_0","x_h", "T", "y"],
        edges=[
            ("x_h", "x_0"),
            ("x_h", "y"),
            ("x_h", "T"),
            ("x_0", "T"),
            ("x_0", "y"),
            ("T", "y"),
        ]
    )

    # draw return a graphviz `dot` object, which jupyter can render
    print(sprinkler.is_valid_backdoor_adjustment_set("T", "y", {"x_0"}))
    print(sprinkler.is_valid_frontdoor_adjustment_set("T", "y", {"x_0"}))


    # nx.draw(sprinkler.dag)
    # plt.show()
def main():
    generate_graph()
if __name__ == '__main__':
    main()