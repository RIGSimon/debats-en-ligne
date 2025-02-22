import json
import networkx as nx
import matplotlib.pyplot as plt
#import pygraphviz

with open('1229.json', 'r') as file:
    data = json.load(file)


nodes = data["nodes"]
edges = data["edges"]

G = nx.DiGraph()

# Add nodes to the graph
for node_id in nodes:
    G.add_node(node_id, text=nodes[node_id]["text"])
# Add edges to the graph
for edge_id, edge_data in edges.items():
    parent_id = edge_data["successor_id"]
    child_id = edge_id
    G.add_edge(parent_id, child_id)
    
    
def extract_limited_tree(graph, root, max_depth, current_depth=0, limited_tree=None):
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
        extract_limited_tree(graph, child, max_depth, current_depth + 1, limited_tree)
    
    return limited_tree
full_tree = G
max_depth = 2
root_node = "1229.0"  # root id (from which to display graph)
limited_tree = extract_limited_tree(full_tree, root_node, max_depth)

plt.figure(figsize=(10, 6))
pos = nx.drawing.nx_agraph.graphviz_layout(limited_tree, prog="twopi")  # "dot" (vertical) or "twopi" (circle)

nx.draw_networkx_nodes(limited_tree, pos, node_size=2000, node_color="lightblue")
nx.draw_networkx_edges(limited_tree, pos, arrowstyle="->", arrowsize=20, edge_color="gray")

labels = {node: f"{node}\n{nodes[node]['text'][:30]}..." for node in limited_tree.nodes()}
nx.draw_networkx_labels(limited_tree, pos, labels, font_size=8, font_color="black")
plt.title(f"Tree Structure (First {max_depth} Levels)", fontsize=15)
plt.axis("off") 
plt.show()