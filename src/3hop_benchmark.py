import os
import random
import statistics
import time

from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("COGNODB_URI"),
    auth=(
        os.getenv("COGNODB_USERNAME"),
        os.getenv("COGNODB_PASSWORD"),
    ),
    max_connection_lifetime=300,
    connection_timeout=30,
)

WARMUP = 5
ITERATIONS = 20

QUERY = """
MATCH (start:User {id: $start_id})-[:VOTED]->()-[:VOTED]->()-[:VOTED]->(n)
RETURN count(DISTINCT n) AS result
LIMIT 1
"""

def run_query(session, node_id):
    return session.run(
        QUERY,
        start_id=node_id,
    ).single()["result"]


try:
    with driver.session() as session:

        result = session.run(
            """
            MATCH (n:User)
            RETURN n.id AS id
            """
        )

        nodes = [record["id"] for record in result]

        random.seed(42)
        random.shuffle(nodes)

        start_ids = nodes[:WARMUP + ITERATIONS]

        print("CognoDB 3-Hop Benchmark")
        print("=" * 30)
        print("Warm-up: 5")
        print("Measured: 20")
        print()

        # Warm-up
        for i, node_id in enumerate(start_ids[:WARMUP], start=1):
            try:
                run_query(session, node_id)
                print(f"Warm-up {i}/{WARMUP}")
            except ServiceUnavailable:
                print("Connection dropped during warm-up.")
                print("3-hop query is too heavy for the current connection.")
                raise

        latencies = []

        for i, node_id in enumerate(
            start_ids[WARMUP:],
            start=1,
        ):
            start = time.perf_counter()

            try:
                run_query(session, node_id)

            except ServiceUnavailable:
                print()
                print("Connection dropped during 3-hop benchmark.")
                print(f"Completed successfully: {len(latencies)}/{ITERATIONS}")
                break

            elapsed = (
                time.perf_counter() - start
            ) * 1000

            latencies.append(elapsed)

            print(
                f"Completed {i}/{ITERATIONS} - "
                f"{elapsed:.3f} ms"
            )

        if not latencies:
            print()
            print("3-hop benchmark FAILED")
            print("=" * 30)
            print("No successful measurements.")
        else:
            values = sorted(latencies)

            def percentile(p):
                index = (len(values) - 1) * p / 100
                low = int(index)
                high = min(low + 1, len(values) - 1)

                if low == high:
                    return values[low]

                fraction = index - low

                return (
                    values[low]
                    + (values[high] - values[low]) * fraction
                )

            print()
            print("3-hop results")
            print("=" * 30)
            print(f"p50:  {percentile(50):.3f} ms")
            print(f"p95:  {percentile(95):.3f} ms")
            print(f"mean: {statistics.mean(latencies):.3f} ms")
            print(f"min:  {min(latencies):.3f} ms")
            print(f"max:  {max(latencies):.3f} ms")
            print(f"samples: {len(latencies)}")

finally:
    driver.close()