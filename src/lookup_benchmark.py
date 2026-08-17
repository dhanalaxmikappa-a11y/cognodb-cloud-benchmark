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

QUERY = """
MATCH (n:User {id: $user_id})
RETURN n.id AS id
"""


def percentile(values, p):
    values = sorted(values)
    index = (len(values) - 1) * p / 100

    lower = int(index)
    upper = min(lower + 1, len(values) - 1)

    if lower == upper:
        return values[lower]

    fraction = index - lower

    return (
        values[lower]
        + (values[upper] - values[lower]) * fraction
    )


def main():
    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD),
    )

    try:
        with driver.session() as session:

            result = session.run(
                """
                MATCH (n:User)
                RETURN n.id AS id
                """
            )

            user_ids = [record["id"] for record in result]

            random.seed(42)
            random.shuffle(user_ids)

            test_ids = user_ids[:WARMUP + ITERATIONS]

            print("CognoDB Point Lookup Benchmark")
            print("=" * 35)
            print(f"Warm-up iterations: {WARMUP}")
            print(f"Measured iterations: {ITERATIONS}")
            print("Random seed: 42")
            print()

            # Warm-up
            for user_id in test_ids[:WARMUP]:
                session.run(
                    QUERY,
                    user_id=user_id,
                ).consume()

            latencies = []

            for user_id in test_ids[WARMUP:]:
                start = time.perf_counter()

                session.run(
                    QUERY,
                    user_id=user_id,
                ).consume()

                elapsed_ms = (
                    time.perf_counter() - start
                ) * 1000

                latencies.append(elapsed_ms)

            print("Point lookup results")
            print("=" * 35)
            print(f"p50:     {percentile(latencies, 50):.3f} ms")
            print(f"p95:     {percentile(latencies, 95):.3f} ms")
            print(f"mean:    {statistics.mean(latencies):.3f} ms")
            print(f"min:     {min(latencies):.3f} ms")
            print(f"max:     {max(latencies):.3f} ms")
            print(f"samples: {len(latencies)}")

    finally:
        driver.close()


if __name__ == "__main__":
    main()