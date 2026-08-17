import os
import time

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE")

DATASET = "data/Wiki-Vote.txt"
BATCH_SIZE = 1000


def read_edges():
    edges = []

    with open(DATASET, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            source, target = line.split()

            edges.append(
                {
                    "source": int(source),
                    "target": int(target),
                }
            )

    return edges


def main():
    edges = read_edges()

    print("Neo4j Wiki-Vote Loader")
    print("=" * 35)
    print(f"Relationships: {len(edges)}")
    print(f"Batch size: {BATCH_SIZE}")
    print()

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD),
    )

    try:
        driver.verify_connectivity()

        # Create index
        with driver.session(database=DATABASE) as session:
            session.run(
                """
                CREATE INDEX user_id_index IF NOT EXISTS
                FOR (n:User) ON (n.id)
                """
            ).consume()

        start_time = time.perf_counter()

        with driver.session(database=DATABASE) as session:

            for start in range(0, len(edges), BATCH_SIZE):

                batch = edges[start:start + BATCH_SIZE]

                session.run(
                    """
                    UNWIND $edges AS edge

                    MERGE (source:User {id: edge.source})
                    MERGE (target:User {id: edge.target})

                    MERGE (source)-[:VOTED]->(target)
                    """,
                    edges=batch,
                ).consume()

                completed = min(
                    start + BATCH_SIZE,
                    len(edges),
                )

                print(
                    f"Loaded {completed}/{len(edges)} relationships"
                )

        elapsed = time.perf_counter() - start_time

        print()
        print("Neo4j Load Results")
        print("=" * 35)
        print(f"Relationships: {len(edges)}")
        print(f"Load time: {elapsed:.3f} seconds")
        print(
            f"Relationships/sec: "
            f"{len(edges) / elapsed:.2f}"
        )

    finally:
        driver.close()


if __name__ == "__main__":
    main()