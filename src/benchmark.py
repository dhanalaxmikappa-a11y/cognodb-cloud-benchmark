import os
import csv
import time

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

OPERATIONS = 1000
WARMUP_OPERATIONS = 100

QUERY = """
MATCH (n:User)
RETURN count(n) AS count
"""


def run_query(session):
    session.run(QUERY).consume()


def run_benchmark():

    print("CognoDB Cloud Benchmark")
    print("=" * 30)
    print(f"Operations: {OPERATIONS}")
    print(f"Warmup operations: {WARMUP_OPERATIONS}")
    print()

    with driver.session() as session:

        print("Running warm-up...")

        for _ in range(WARMUP_OPERATIONS):
            run_query(session)

        print("Warm-up complete.")
        print("Running benchmark...")

        start_time = time.perf_counter()

        for i in range(OPERATIONS):
            run_query(session)

            if (i + 1) % 100 == 0:
                print(f"Completed {i + 1}/{OPERATIONS}")

        end_time = time.perf_counter()

    elapsed = end_time - start_time

    operations_per_second = OPERATIONS / elapsed
    average_ms = (elapsed / OPERATIONS) * 1000

    print()
    print("Benchmark Results")
    print("=" * 30)
    print(f"Operations: {OPERATIONS}")
    print(f"Execution time: {elapsed:.3f} seconds")
    print(f"Average latency: {average_ms:.3f} ms")
    print(f"Operations/sec: {operations_per_second:.2f}")

    output_file = "benchmark_results.csv"

    file_exists = os.path.exists(output_file)

    with open(output_file, "a", newline="") as file:

        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "operations",
                "execution_time_seconds",
                "average_latency_ms",
                "operations_per_second"
            ])

        writer.writerow([
            OPERATIONS,
            elapsed,
            average_ms,
            operations_per_second
        ])

    print()
    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    try:
        run_benchmark()
    finally:
        driver.close()