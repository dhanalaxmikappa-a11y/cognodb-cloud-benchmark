import os
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
MATCH (n:User)
RETURN count(n) AS user_count
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

            print("Neo4j Aggregation Benchmark")
            print("=" * 35)
            print(
                f"Warm-up iterations: {WARMUP}"
            )
            print(
                f"Measured iterations: {ITERATIONS}"
            )
            print()

            print("Running warm-up...")

            for i in range(WARMUP):

                session.run(QUERY).consume()

                if (i + 1) % 5 == 0:
                    print(
                        f"Warm-up {i + 1}/{WARMUP}"
                    )

            print("Warm-up complete.")
            print()

            latencies = []

            print("Running benchmark...")

            user_count = None

            for i in range(ITERATIONS):

                start = time.perf_counter()

                result = session.run(
                    QUERY
                )

                record = result.single()

                elapsed_ms = (
                    time.perf_counter()
                    - start
                ) * 1000

                latencies.append(elapsed_ms)

                user_count = record["user_count"]

                if (i + 1) % 10 == 0:
                    print(
                        f"Completed {i + 1}/{ITERATIONS} "
                        f"- {elapsed_ms:.3f} ms"
                    )

            print()
            print("Aggregation Results")
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
            print()
            print(
                f"Users counted: {user_count}"
            )

    finally:
        driver.close()


if __name__ == "__main__":
    main()