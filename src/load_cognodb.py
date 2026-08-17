import os
import time
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")

DATASET = Path("data/Wiki-Vote.txt")
BATCH_SIZE = 1000


def load_cognodb():
    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD),
    )

    rows = []
    relationships = 0
    nodes = set()

    start_time = time.perf_counter()

    try:
        with DATASET.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                source, target = map(int, line.split())

                nodes.add(source)
                nodes.add(target)

                rows.append(
                    {
                        "source": source,
                        "target": target,
                    }
                )

                if len(rows) >= BATCH_SIZE:
                    with driver.session() as session:
                        session.run(
                            """
                            UNWIND $rows AS row
                            MERGE (a:User {id: row.source})
                            MERGE (b:User {id: row.target})
                            MERGE (a)-[:VOTED]->(b)
                            """,
                            rows=rows,
                        ).consume()

                    relationships += len(rows)
                    print(
                        f"Loaded {relationships}/{103689} relationships",
                        flush=True,
                    )
                    rows.clear()

            if rows:
                with driver.session() as session:
                    session.run(
                        """
                        UNWIND $rows AS row
                        MERGE (a:User {id: row.source})
                        MERGE (b:User {id: row.target})
                        MERGE (a)-[:VOTED]->(b)
                        """,
                        rows=rows,
                    ).consume()

                relationships += len(rows)

        elapsed = time.perf_counter() - start_time

        print()
        print("CognoDB full dataset load complete")
        print("=" * 40)
        print(f"Nodes discovered: {len(nodes)}")
        print(f"Relationships processed: {relationships}")
        print(f"Load time: {elapsed:.3f} seconds")
        print(f"Relationships/sec: {relationships / elapsed:.2f}")

    finally:
        driver.close()


if __name__ == "__main__":
    load_cognodb()