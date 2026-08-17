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
MATCH (n:User)
WHERE n.id = $user_id
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

            user_ids = [
                record["id"]
                for record in result
            ]

            random.seed(42)
            random.shuffle(user_ids)

            test_ids = user_ids[
                :WARMUP + ITERATIONS
            ]

            print("CognoDB Indexed Lookup Benchmark")
            print("=" * 40)
            print(f"Warm-up iterations: {WARMUP}")
            print(f"Measured iterations: {ITERATIONS}")
            print("Random seed: 42")
            print("Index: User.id (RANGE)")
            print()

            print("Running warm-up...")

            for i, user_id in enumerate(
                test_ids[:WARMUP],
                start=1,
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

            print("Running benchmark...")

            latencies = []

            for i, user_id in enumerate(
                test_ids[WARMUP:],
                start=1,
            ):

                start = time.perf_counter()

                session.run(
                    QUERY,
                    user_id=user_id,
                ).consume()

                elapsed_ms = (
                    time.perf_counter() - start
                ) * 1000

                latencies.append(elapsed_ms)

                if i % 10 == 0:
                    print(
                        f"Completed {i}/{ITERATIONS}"
                    )

            print()
            print("Indexed Lookup Results")
            print("=" * 40)

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
                f"samples: "
                f"{len(latencies)}"
            )

    finally:
        driver.close()


if __name__ == "__main__":
    main()