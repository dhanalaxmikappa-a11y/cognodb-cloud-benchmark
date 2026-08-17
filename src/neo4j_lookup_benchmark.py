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

    return values[lower] + (
        values[upper] - values[lower]
    ) * fraction


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

            result = session.run(
                """
                MATCH (n:User)
                RETURN n.id AS id
                """
            )

            user_ids = [
                record["id"]
                for record in result
            ]

            random.seed(42)
            random.shuffle(user_ids)

            test_ids = user_ids[
                :WARMUP + ITERATIONS
            ]

            print("Neo4j Point Lookup Benchmark")
            print("=" * 35)
            print(
                f"Warm-up iterations: {WARMUP}"
            )
            print(
                f"Measured iterations: {ITERATIONS}"
            )
            print("Random seed: 42")
            print()

            print("Running warm-up...")

            for i, user_id in enumerate(
                test_ids[:WARMUP], 1
            ):

                session.run(
                    QUERY,
                    user_id=user_id,
                ).consume()

                if i % 5 == 0:
                    print(
                        f"Warm-up {i}/{WARMUP}"
                    )

            print("Warm-up complete.")
            print()

            latencies = []

            print("Running benchmark...")

            for i, user_id in enumerate(
                test_ids[WARMUP:], 1
            ):

                start = time.perf_counter()

                session.run(
                    QUERY,
                    user_id=user_id,
                ).consume()

                elapsed_ms = (
                    time.perf_counter()
                    - start
                ) * 1000

                latencies.append(elapsed_ms)

                if i % 10 == 0:
                    print(
                        f"Completed {i}/{ITERATIONS} "
                        f"- {elapsed_ms:.3f} ms"
                    )

            print()
            print("Point Lookup Results")
            print("=" * 35)
            print(
                f"p50:     "
                f"{percentile(latencies, 50):.3f} ms"
            )
            print(
                f"p95:     "
                f"{percentile(latencies, 95):.3f} ms"
            )
            print(
                f"mean:    "
                f"{statistics.mean(latencies):.3f} ms"
            )
            print(
                f"min:     "
                f"{min(latencies):.3f} ms"
            )
            print(
                f"max:     "
                f"{max(latencies):.3f} ms"
            )
            print(
                f"samples: {len(latencies)}"
            )

    finally:
        driver.close()


if __name__ == "__main__":
    main()