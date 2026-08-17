import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("COGNODB_URI"),
    auth=(
        os.getenv("COGNODB_USERNAME"),
        os.getenv("COGNODB_PASSWORD"),
    ),
)

try:
    with driver.session() as session:
        session.run("MATCH (n:User) DETACH DELETE n").consume()
        print("CognoDB benchmark data cleared.")
finally:
    driver.close()