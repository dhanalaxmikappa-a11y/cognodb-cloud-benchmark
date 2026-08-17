import os
import random
import statistics
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE")

CONCURRENCY = 10
DURATION_SECONDS = 30

READ_PERCENT = 80
WRITE_PERCENT = 20


READ_QUERY = """
MATCH (n:User {id: $user_id})
RETURN n.id AS id
"""


WRITE_QUERY = """
MATCH (n:User {id: $user_id})
SET n.benchmark_value = $value
RETURN n.id AS id
"""


def worker(driver, user_ids, stop_event, results):

    local_random = random.Random(
        threading.current_thread().ident
    )

    while not stop_event.is_set():

        user_id = local_random.choice(user_ids)

        is_read = (
            local_random.random() * 100
            < READ_PERCENT
        )

        start = time.perf_counter()

        try:

            with driver.session(
                database=DATABASE
            ) as session:

                if is_read:

                    session.run(
                        READ_QUERY,
                        user_id=user_id,
                    ).consume()

                else:

                    session.run(
                        WRITE_QUERY,
                        user_id=user_id,
                        value=local_random.randint(
                            1,
                            1000000,
                        ),
                    ).consume()

            elapsed_ms = (
                time.perf_counter()
                - start
            ) * 1000

            results.append(
                ("success", elapsed_ms)
            )

        except Exception as error:

            results.append(
                ("failed", str(error))
            )


def main():

    print("Neo4j Mixed Read/Write Benchmark")
    print("=" * 45)
    print(f"Concurrency: {CONCURRENCY}")
    print(
        f"Duration: {DURATION_SECONDS} seconds"
    )
    print(f"Read mix: {READ_PERCENT}%")
    print(
        f"Write mix: {WRITE_PERCENT}%"
    )
    print()

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD),
        max_connection_pool_size=CONCURRENCY + 5,
    )

    try:

        driver.verify_connectivity()

        with driver.session(
            database=DATABASE
        ) as session:

            records = session.run(
                """
                MATCH (n:User)
                RETURN n.id AS id
                """
            )

            user_ids = [
                record["id"]
                for record in records
            ]

        results = []
        stop_event = threading.Event()

        print("Starting benchmark...")

        start_time = time.perf_counter()

        with ThreadPoolExecutor(
            max_workers=CONCURRENCY
        ) as executor:

            futures = [
                executor.submit(
                    worker,
                    driver,
                    user_ids,
                    stop_event,
                    results,
                )
                for _ in range(CONCURRENCY)
            ]

            time.sleep(DURATION_SECONDS)

            stop_event.set()

            for future in futures:
                future.result()

        elapsed = (
            time.perf_counter()
            - start_time
        )

        successful = [
            latency
            for status, latency in results
            if status == "success"
        ]

        failed = len(results) - len(successful)

        total_ops = len(results)

        throughput = (
            total_ops / elapsed
            if elapsed > 0
            else 0
        )

        average_latency = (
            statistics.mean(successful)
            if successful
            else 0
        )

        min_latency = (
            min(successful)
            if successful
            else 0
        )

        max_latency = (
            max(successful)
            if successful
            else 0
        )

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
            f"Successful ops:    {len(successful)}"
        )
        print(
            f"Failed ops:        {failed}"
        )
        print(
            f"Total ops:         {total_ops}"
        )
        print(
            f"Throughput:        {throughput:.2f} ops/sec"
        )
        print(
            f"Average latency:   "
            f"{average_latency:.3f} ms"
        )
        print(
            f"Min latency:       "
            f"{min_latency:.3f} ms"
        )
        print(
            f"Max latency:       "
            f"{max_latency:.3f} ms"
        )

        print()
        print("Benchmark complete.")

    finally:

        driver.close()


if __name__ == "__main__":
    main()