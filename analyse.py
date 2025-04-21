from collections import defaultdict
from itertools import combinations
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

nx.write_graphml(G, "graph.graphml")  # or nx.write_graphml(G, "graph.graphml")

def condensed_graph(G):
    G_copy = G.copy()  # Makes a shallow copy of the graph structure and attributes

    nodes_to_remove = [
        node for node in G_copy.nodes()
        if G_copy.in_degree(node) + G_copy.out_degree(node) == 1
    ]

    G_copy.remove_nodes_from(nodes_to_remove)
    return G_copy

condensed = condensed_graph(G)

nx.write_graphml(condensed, "condensed_graph.graphml")  # or nx.write_graphml(G, "graph.graphml")
# Done! Now G is your NetworkX graph.
print(f"Graph type: {type(G)}")
print(f"Nodes: {G.number_of_nodes()}")
print(f"Edges: {G.number_of_edges()}")

# Optional: check degree statistics
degrees = [deg for _, deg in G.degree()]
print(f"Average degree: {sum(degrees) / len(degrees):.2f}" if degrees else "No nodes to calculate degree.")

def build_co_citation_network(G):
    co_citation = nx.Graph()  # undirected

    # For every node, get all the nodes it points to
    citations_by_source = defaultdict(list)

    for source, target in G.edges():
        citations_by_source[source].append(target)

    # For each source node, look at all pairs of citations it made
    for cited_nodes in citations_by_source.values():
        for u, v in combinations(set(cited_nodes), 2):  # remove dupes
            if co_citation.has_edge(u, v):
                co_citation[u][v]["weight"] += 1
            else:
                co_citation.add_edge(u, v, weight=1)

    return co_citation

co_citation_graph = build_co_citation_network(G)
nx.write_graphml(co_citation_graph, "co_citation_graph.graphml")