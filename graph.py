import json
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
import random

class DebateGraph:
    def __init__(self, filename, nb, strategy="random"):
        with open(filename, 'r') as file:
            data = json.load(file)

        self.nodes = data["nodes"]
        self.edges = data["edges"]
        self.G = nx.DiGraph()

        # Add nodes to the graph with level information
        for node_id, node_data in self.nodes.items():
            self.G.add_node(node_id, **node_data, level=-1)  # Initialize with -1

        # Root node
        self.root = [n for n in self.nodes if self.G.in_degree(n) == 0][0]
        self.G.nodes[self.root]['level'] = 0  # Set root level to 0

        # Add edges to the graph and calculate levels
        self.edge_colors = []
        for edge_id, edge_data in self.edges.items():
            parent_id = edge_data["successor_id"]
            child_id = edge_id
            self.G.add_edge(parent_id, child_id, **edge_data)
            
            # Set child level (parent level + 1)
            if 'level' not in self.G.nodes[child_id] or self.G.nodes[child_id]['level'] == -1:
                self.G.nodes[child_id]['level'] = self.G.nodes[parent_id]['level'] + 1

            # Edge colors
            relation = edge_data["relation"]
            if relation == 1:
                self.edge_colors.append("green")
            elif relation == -1:
                self.edge_colors.append("red")
            else:
                self.edge_colors.append("black")

        # Choose the order strategy
        if strategy == "random":
            self.main_arg, self.order = random_order(self.G, self.root)
        elif strategy == "BFS":
            self.main_arg, self.order = BFS_order(self.G, self.root)
        elif strategy == "DFS":
            self.main_arg, self.order = DFS_order(self.G, self.root)
        elif strategy == "priority":
            self.main_arg, self.order = priority_order(self.G, self.root)
        else:
            raise ValueError("Unknown strategy")
        
        if nb != -1:
            self.order = self.order[:nb * 2]


    def extract_limited_tree(self, graph, root, max_depth, current_depth=0, limited_tree=None):
        """
        Retourne le graphe associé jusqu'à la profondeur max_depth
        """
        if limited_tree is None:
            limited_tree = nx.DiGraph()
        
        if current_depth > max_depth:
            return limited_tree
        
        limited_tree.add_node(root, text=graph.nodes[root]["text"])
        
        for child in graph.successors(root):
            limited_tree.add_edge(root, child)
            self.extract_limited_tree(graph, child, max_depth, current_depth + 1, limited_tree)
        
        return limited_tree


    def display_graph(self, G, title="Graphe d'arguments"):
        plt.figure(figsize=(10, 6))
        pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
        nx.draw_networkx_nodes(G, pos, node_size=2000, node_color="lightblue")
        nx.draw_networkx_edges(G, pos, arrowstyle="->", arrowsize=20, edge_color=self.edge_colors)

        labels = {node: f"{node}\n{self.nodes[node]['text'][:30]}..." for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=8, font_color="black")
        plt.title(title, fontsize=15)
        plt.axis("off") 
        plt.show()


def BFS_order(graph, root):
    """
    Parcours BFS pour établir l'ordre complet des comparaisons
    """
    root_succ = [succ for succ in graph.successors(root)][0]
    main_arg_succ = [succ for succ in graph.successors(root_succ)][0]

    queue = deque([main_arg_succ])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for successor in graph.successors(node):
            queue.append(successor)

    return root_succ, order


def random_order(graph, root):
    """
    Parcours random pour établir l'ordre complet des comparaisons (mélangé)
    """
    root_succ, node_list = BFS_order(graph, root)
    random.shuffle(node_list)  # Mélange la liste complète
    return root_succ, node_list


def DFS_order(graph, root):
    """
    Parcours DFS pour établir l'ordre complet des comparaisons
    """
    root_succ = [succ for succ in graph.successors(root)][0]
    stack = [root_succ]
    order = []

    while stack:
        node = stack.pop()
        order.append(node)
        for successor in reversed(list(graph.successors(node))):  # Reverse to process left-to-right
            stack.append(successor)

    return root_succ, order


def priority_order(graph, root):
    """
    Parcours par priorité qui maintient l'ordre BFS mais alterne les relations
    Les noeuds avec relation 1 et -1 sont alternés quand c'est possible
    """
    root_succ = [succ for succ in graph.successors(root)][0]
    nodes_bfs_order = BFS_order(graph, root)[1]  # Get nodes in BFS order
    
    # Separate nodes by their incoming edge relation
    nodes_relation_1 = []
    nodes_relation_minus1 = []
    nodes_other = []
    
    for node in nodes_bfs_order:
        predecessors = list(graph.predecessors(node))
        if not predecessors:
            nodes_other.append(node)
            continue
            
        edge_data = graph.get_edge_data(predecessors[0], node)
        if edge_data and edge_data.get("relation", 0) == 1:
            nodes_relation_1.append(node)
        elif edge_data and edge_data.get("relation", 0) == -1:
            nodes_relation_minus1.append(node)
        """
        else:
            nodes_other.append(node)
        """
    
    # Interleave the 1 and -1 nodes
    interleaved_nodes = []
    for r1, r_minus1 in zip(nodes_relation_1, nodes_relation_minus1):
        interleaved_nodes.append(r1)
        interleaved_nodes.append(r_minus1)
    
    # Add any remaining nodes (the zip stops at the shorter list)
    if len(nodes_relation_1) > len(nodes_relation_minus1):
        interleaved_nodes.extend(nodes_relation_1[len(nodes_relation_minus1):])
    else:
        interleaved_nodes.extend(nodes_relation_minus1[len(nodes_relation_1):])
    
    # Add nodes with other/unknown relations at the end
    interleaved_nodes.extend(nodes_other)
    
    return root_succ, interleaved_nodes


if __name__ == '__main__':
    filename = "./data/1229.json"
    Graph = DebateGraph(filename, nb=10, strategy="priority")
    Graph.display_graph(Graph.G)