import time


def run_benchmark():
    print("Cognodb Cloud Benchmark")
    print("=" * 30)

    start_time = time.perf_counter()

    # Benchmark workload
    for _ in range(1_000_000):
        pass

    end_time = time.perf_counter()

    elapsed = end_time - start_time

    print(f"Execution time: {elapsed:.6f} seconds")


def main():
    run_benchmark()


if __name__ == "__main__":
    main()