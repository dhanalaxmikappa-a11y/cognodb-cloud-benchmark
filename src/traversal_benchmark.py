import os
import random
import statistics
import time

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")

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
    # Warm-up
    for start_id in start_ids[:WARMUP]:
        session.run(
            query,
            start_id=start_id,
        ).consume()

    latencies = []

    for start_id in start_ids[WARMUP:]:
        start = time.perf_counter()

        session.run(
            query,
            start_id=start_id,
        ).consume()

        elapsed_ms = (
            time.perf_counter() - start
        ) * 1000

        latencies.append(elapsed_ms)

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
        with driver.session() as session:
            all_nodes = get_start_nodes(session)

            random.seed(42)
            random.shuffle(all_nodes)

            start_ids = all_nodes[: WARMUP + ITERATIONS]

            print("CognoDB Traversal Benchmark")
            print("=" * 35)
            print(f"Warm-up iterations: {WARMUP}")
            print(f"Measured iterations: {ITERATIONS}")
            print(f"Random seed: 42")
            print()

            for name, query in QUERIES.items():
                result = measure_query(
                    session,
                    query,
                    start_ids,
                )

                print(name)
                print(f"  p50:   {result['p50_ms']:.3f} ms")
                print(f"  p95:   {result['p95_ms']:.3f} ms")
                print(f"  mean:  {result['mean_ms']:.3f} ms")
                print(f"  min:   {result['min_ms']:.3f} ms")
                print(f"  max:   {result['max_ms']:.3f} ms")
                print(f"  samples: {result['samples']}")
                print()

    finally:
        driver.close()


if __name__ == "__main__":
    main()