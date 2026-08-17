import os
from pathlib import Path

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

DATASET = Path("data/Wiki-Vote.txt")

try:
    rows = []

    with DATASET.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            source, target = map(int, line.split())
            rows.append({"source": source, "target": target})

            if len(rows) == 1000:
                break

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

    print("Test load successful!")
    print(f"Relationships attempted: {len(rows)}")

finally:
    driver.close()