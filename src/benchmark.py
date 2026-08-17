import csv
import os
import time
import config


def run_benchmark():
    print("Cognodb Cloud Benchmark")
    print("=" * 30)
    print(f"Operations: {config.OPERATIONS}")
    print(f"Warmup operations: {config.WARMUP_OPERATIONS}")

    # Warmup
    for _ in range(config.WARMUP_OPERATIONS):
        pass

    # Start benchmark
    start_time = time.perf_counter()

    for _ in range(config.OPERATIONS):
        pass

    # End benchmark
    end_time = time.perf_counter()

    elapsed = end_time - start_time

    print(f"Execution time: {elapsed:.6f} seconds")

    # Create CSV file with header if it does not exist
    file_exists = os.path.exists(config.OUTPUT_FILE)

    with open(config.OUTPUT_FILE, "a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "operations",
                "execution_time_seconds"
            ])

        writer.writerow([
            config.OPERATIONS,
            elapsed
        ])


def main():
    run_benchmark()


if __name__ == "__main__":
    main()