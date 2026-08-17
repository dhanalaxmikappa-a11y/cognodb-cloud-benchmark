import os
import random
import statistics
import time

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE")

WARMUP = 20
ITERATIONS = 100


QUERIES = {
    "1-hop": """
        MATCH (start:User {id: $start_id})-[:VOTED]->(n)
        RETURN count(n) AS result
    """,
    "2-hop": """
        MATCH (start:User {id: $start_id})-[:VOTED*2]->(n)
        RETURN count(n) AS result
    """,
    "3-hop": """
        MATCH (start:User {id: $start_id})-[:VOTED*3]->(n)
        RETURN count(n) AS result
    """,
}


def percentile(values, p):
    values = sorted(values)

    index = (len(values) - 1) * p / 100

    lower = int(index)
    upper = min(lower + 1, len(values) - 1)

    if lower == upper:
        return values[lower]

    fraction = index - lower

    return values[lower] + (
        values[upper] - values[lower]
    ) * fraction


def get_start_nodes(session):
    result = session.run(
        """
        MATCH (n:User)
        RETURN n.id AS id
        """
    )

    return [record["id"] for record in result]


def measure_query(session, query, start_ids):

    print("Running warm-up...")

    for i, start_id in enumerate(start_ids[:WARMUP], 1):

        session.run(
            query,
            start_id=start_id,
        ).consume()

        if i % 5 == 0:
            print(f"Warm-up {i}/{WARMUP}")

    print("Warm-up complete.")
    print()

    latencies = []

    print("Running benchmark...")

    for i, start_id in enumerate(
        start_ids[WARMUP:], 1
    ):

        start = time.perf_counter()

        session.run(
            query,
            start_id=start_id,
        ).consume()

        elapsed_ms = (
            time.perf_counter() - start
        ) * 1000

        latencies.append(elapsed_ms)

        if i % 10 == 0:
            print(
                f"Completed {i}/{ITERATIONS} - "
                f"{elapsed_ms:.3f} ms"
            )

    return {
        "p50_ms": percentile(latencies, 50),
        "p95_ms": percentile(latencies, 95),
        "min_ms": min(latencies),
        "max_ms": max(latencies),
        "mean_ms": statistics.mean(latencies),
        "samples": len(latencies),
    }


def main():

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD),
    )

    try:

        driver.verify_connectivity()

        with driver.session(
            database=DATABASE
        ) as session:

            all_nodes = get_start_nodes(session)

            random.seed(42)
            random.shuffle(all_nodes)

            start_ids = all_nodes[
                :WARMUP + ITERATIONS
            ]

            print("Neo4j Traversal Benchmark")
            print("=" * 35)
            print(
                f"Warm-up iterations: {WARMUP}"
            )
            print(
                f"Measured iterations: {ITERATIONS}"
            )
            print("Random seed: 42")
            print()

            for name, query in QUERIES.items():

                print(name)
                print("=" * 30)

                result = measure_query(
                    session,
                    query,
                    start_ids,
                )

                print()
                print(f"{name} results")
                print("=" * 30)
                print(
                    f"p50:   "
                    f"{result['p50_ms']:.3f} ms"
                )
                print(
                    f"p95:   "
                    f"{result['p95_ms']:.3f} ms"
                )
                print(
                    f"mean:  "
                    f"{result['mean_ms']:.3f} ms"
                )
                print(
                    f"min:   "
                    f"{result['min_ms']:.3f} ms"
                )
                print(
                    f"max:   "
                    f"{result['max_ms']:.3f} ms"
                )
                print(
                    f"samples: "
                    f"{result['samples']}"
                )
                print()

    finally:
        driver.close()


if __name__ == "__main__":
    main()