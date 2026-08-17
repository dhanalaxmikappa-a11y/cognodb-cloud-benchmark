import os
import random
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")

CONCURRENCY = 10
DURATION_SECONDS = 30

READ_PERCENT = 80
WRITE_PERCENT = 20

READ_QUERY = """
MATCH (n:User)
RETURN count(n) AS count
"""

WRITE_QUERY = """
MERGE (a:BenchmarkUser {id: $source})
MERGE (b:BenchmarkUser {id: $target})
MERGE (a)-[:BENCHMARK_VOTED]->(b)
"""


def worker(worker_id):
    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD),
    )

    random.seed(42 + worker_id)

    successful = 0
    failed = 0
    latencies = []

    try:
        with driver.session() as session:

            while time.perf_counter() < END_TIME:

                operation = random.randint(1, 100)

                start = time.perf_counter()

                try:

                    if operation <= READ_PERCENT:

                        session.run(
                            READ_QUERY
                        ).consume()

                    else:

                        source = (
                            worker_id * 100000
                            + random.randint(1, 10000)
                        )

                        target = (
                            worker_id * 100000
                            + random.randint(1, 10000)
                        )

                        session.run(
                            WRITE_QUERY,
                            source=source,
                            target=target,
                        ).consume()

                    elapsed_ms = (
                        time.perf_counter() - start
                    ) * 1000

                    latencies.append(elapsed_ms)
                    successful += 1

                except Exception:
                    failed += 1

    finally:
        driver.close()

    return {
        "successful": successful,
        "failed": failed,
        "latencies": latencies,
    }


def main():

    global END_TIME

    print("CognoDB Mixed Read/Write Benchmark")
    print("=" * 45)
    print(f"Concurrency: {CONCURRENCY}")
    print(f"Duration: {DURATION_SECONDS} seconds")
    print(f"Read mix: {READ_PERCENT}%")
    print(f"Write mix: {WRITE_PERCENT}%")
    print()

    print("Starting benchmark...")

    start_time = time.perf_counter()

    END_TIME = start_time + DURATION_SECONDS

    results = []

    with ThreadPoolExecutor(
        max_workers=CONCURRENCY
    ) as executor:

        futures = [
            executor.submit(worker, worker_id)
            for worker_id in range(CONCURRENCY)
        ]

        for future in as_completed(futures):
            results.append(future.result())

    end_time = time.perf_counter()

    elapsed = end_time - start_time

    successful = sum(
        result["successful"]
        for result in results
    )

    failed = sum(
        result["failed"]
        for result in results
    )

    all_latencies = []

    for result in results:
        all_latencies.extend(
            result["latencies"]
        )

    total_operations = successful + failed

    throughput = successful / elapsed

    print()
    print("Mixed Workload Results")
    print("=" * 45)

    print(
        f"Concurrency:       {CONCURRENCY}"
    )

    print(
        f"Duration:          {elapsed:.3f} seconds"
    )

    print(
        f"Successful ops:    {successful}"
    )

    print(
        f"Failed ops:        {failed}"
    )

    print(
        f"Total ops:         {total_operations}"
    )

    print(
        f"Throughput:        {throughput:.2f} ops/sec"
    )

    if all_latencies:

        print(
            f"Average latency:   "
            f"{statistics.mean(all_latencies):.3f} ms"
        )

        print(
            f"Min latency:       "
            f"{min(all_latencies):.3f} ms"
        )

        print(
            f"Max latency:       "
            f"{max(all_latencies):.3f} ms"
        )

    print()
    print("Benchmark complete.")


if __name__ == "__main__":
    main()