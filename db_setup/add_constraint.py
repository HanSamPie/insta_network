from neo4j import GraphDatabase

# Neo4j connection settings
URI = "bolt://localhost:7687"  # Adjust if using a different address
AUTH = ("neo4j", "password")  # Replace with your credentials

# Queries to create constraints and indexes
QUERIES = [
    "MATCH (a:Account) DETACH DELETE a",
    "CREATE CONSTRAINT unique_username FOR (a:Account) REQUIRE a.username IS UNIQUE;",
    "CREATE INDEX account_follows_idx FOR (a:Account) ON (a.following_count);",
    "CREATE INDEX account_followers_idx FOR (a:Account) ON (a.followers_count);",
]

def apply_constraints(driver):
    with driver.session() as session:
        for query in QUERIES:
            session.run(query)
            print(f"Applied: {query}")

# Connect to Neo4j and apply constraints
with GraphDatabase.driver(URI, auth=AUTH) as driver:
    apply_constraints(driver)