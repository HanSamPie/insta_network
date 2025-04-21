from neo4j import GraphDatabase
import networkx as nx

# Connect to Neo4j
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password")
driver = GraphDatabase.driver(URI, auth=AUTH)

def load_graph(tx):
    # Example: get all nodes and relationships
    result = tx.run("""
        MATCH (a)-[r]->(b)
        RETURN a, r, b
    """)
    
    G = nx.DiGraph()  # or nx.Graph() for undirected

    for record in result:
        a = record["a"]
        b = record["b"]
        r = record["r"]
        
        a_id = a.element_id
        b_id = b.element_id

        # Add nodes with their properties
        G.add_node(a_id, **a._properties)
        G.add_node(b_id, **b._properties)

        # Add edge with its properties
        G.add_edge(a_id, b_id, **r._properties)

    return G

# Run the transaction
with driver.session() as session:
    G = session.execute_read(load_graph)

# Done! Now G is your NetworkX graph.
print(f"Graph type: {type(G)}")
print(f"Nodes: {G.number_of_nodes()}")
print(f"Edges: {G.number_of_edges()}")

# Optional: check degree statistics
degrees = [deg for _, deg in G.degree()]
print(f"Average degree: {sum(degrees) / len(degrees):.2f}" if degrees else "No nodes to calculate degree.")

nx.write_gexf(G, "graph.gexf")  # or nx.write_graphml(G, "graph.graphml")


nodes_to_remove = [
    node for node in G.nodes()
    if G.in_degree(node) + G.out_degree(node) == 1
]

G.remove_nodes_from(nodes_to_remove)

nx.write_gexf(G, "condensed_graph.gexf")  # or nx.write_graphml(G, "graph.graphml")
# Done! Now G is your NetworkX graph.
print(f"Graph type: {type(G)}")
print(f"Nodes: {G.number_of_nodes()}")
print(f"Edges: {G.number_of_edges()}")

# Optional: check degree statistics
degrees = [deg for _, deg in G.degree()]
print(f"Average degree: {sum(degrees) / len(degrees):.2f}" if degrees else "No nodes to calculate degree.")
