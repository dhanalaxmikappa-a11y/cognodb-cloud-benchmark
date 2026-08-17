import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()


URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")


def test_connection():
    if not URI or not USERNAME or not PASSWORD:
        raise RuntimeError(
            "CognoDB credentials are missing from the .env file."
        )

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:
        driver.verify_connectivity()

        with driver.session() as session:
            result = session.run("RETURN 1 AS connected")
            record = result.single()

            print("CognoDB connection successful!")
            print(f"Test query result: {record['connected']}")

    finally:
        driver.close()


if __name__ == "__main__":
    test_connection()