import json
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
import random


class DebateGraph:
    def __init__(self, filename, nb):

        with open(filename, 'r') as file:
            data = json.load(file)

        self.nodes = data["nodes"]
        self.edges = data["edges"]
        self.G = nx.DiGraph()

        self.G.graph["graph"] = {"rankdir": "TB"}

        # Add nodes to the graph
        for node_id, node_data in self.nodes.items():
            self.G.add_node(node_id, **node_data)
        
        # Root node
        self.root = [n for n in self.nodes if self.G.in_degree(n) == 0][0]

        # Add edges to the graph
        self.edge_colors = []
        for edge_id, edge_data in self.edges.items():
            parent_id = edge_data["successor_id"]
            child_id = edge_id
            self.G.add_edge(parent_id, child_id, **edge_data)

            # Edge colors : 1 pour / -1 contre
            relation = edge_data["relation"]
            if relation == 1:
                self.edge_colors.append("green")
            elif relation == -1:
                self.edge_colors.append("red")
            else:
                self.edge_colors.append("black")

        # BFS
        # self.main_arg, self.order = BFS_order(self.G, self.root)

        # Random
        self.main_arg, self.order = random_order(self.G, self.root, nb)


    def extract_limited_tree(self, graph, root, max_depth, current_depth=0, limited_tree=None):
        """
        Retourne le graphe associé jusqu'à la profondeur max_depth
        """

        if limited_tree is None:
            limited_tree = nx.DiGraph()
        
        # Stop if we exceed the max depth
        if current_depth > max_depth:
            return limited_tree
        
        # Add the current node to the limited tree
        limited_tree.add_node(root, text=graph.nodes[root]["text"])
        
        # Recursively add children
        for child in graph.successors(root):
            limited_tree.add_edge(root, child)
            self.extract_limited_tree(graph, child, max_depth, current_depth + 1, limited_tree)
        
        return limited_tree


    def display_graph(self, G, title="Graphe d'arguments"):
        plt.figure(figsize=(10, 6))

        # pos = nx.drawing.nx_agraph.graphviz_layout(limited_tree, prog="twopi")  # "dot" (vertical) or "twopi" (circle)
        pos = nx.nx_agraph.graphviz_layout(G, prog="dot") # Arborescence

        nx.draw_networkx_nodes(G, pos, node_size=2000, node_color="lightblue")
        nx.draw_networkx_edges(G, pos, arrowstyle="->", arrowsize=20, edge_color=self.edge_colors)

        labels = {node: f"{node}\n{self.nodes[node]['text'][:30]}..." for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=8, font_color="black")
        plt.title(title, fontsize=15)
        plt.axis("off") 
        plt.show()


def BFS_order(graph, root):
    """
    Parcours BFS pour établir l'ordre des comparaisons
    Renvoie l'id de la question principale et l'ordre des noeuds à parcourir
    """

    # La racine (1229.0) a du texte vide donc on prend son successeur (1229.1)
    root_succ = [succ for succ in graph.successors(root)][0]

    # 1229.1 semble etre la question principale donc on prend son successeur (1229.2)
    main_arg_succ = [succ for succ in graph.successors(root_succ)][0]

    queue = deque([main_arg_succ])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)

        for successor in graph.successors(node):
            queue.append(successor)


    return root_succ, order


def random_order(graph, root, nb):
    """
    Parcours random pour établir l'ordre des comparaisons
    Renvoie l'id de la question principale et l'ordre des noeuds à parcourir
    """

    root_succ, list = BFS_order(graph, root)
    order = []

    n = len(list)
    nb_elem = n
    nb_comp = nb * 2

    if (nb == -1):
        nb_comp = n

    for _ in range (nb_comp):
        i = random.randint(0, nb_elem-1)
        nb_elem = nb_elem - 1
        order.append(list[i])
        list.pop(i)

    return root_succ, order


if __name__ == '__main__':
    filename = "./data/1229.json" # A tester sur d'autres fichiers
    Graph = DebateGraph(filename)

    full_tree = Graph.G
    root_node = Graph.root
    max_depth = 2 # Profondeur de l'arbre a afficher
    limited_tree = Graph.extract_limited_tree(full_tree, root_node, max_depth)

    Graph.display_graph(limited_tree, f"Tree Structure (First {max_depth} Levels)") # Pour afficher qu'une partie de l'arbre
    # Graph.display_graph(full_tree) # Pour afficher l'arbre en entier