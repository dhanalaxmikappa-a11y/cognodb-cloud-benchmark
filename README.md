# CognoDB Cloud Benchmark

A Python-based benchmark project for evaluating graph data loading and traversal performance on CognoDB Cloud using the Neo4j-compatible Bolt driver.

## Overview

This project loads the Wiki-Vote graph dataset into CognoDB Cloud and measures database performance using different workloads.

The benchmark evaluates:

* Full dataset loading
* Database connectivity
* 1-hop graph traversal
* 2-hop graph traversal
* 3-hop graph traversal
* 1,000 database operations
* Query latency and throughput

## Dataset

The benchmark uses the **Wiki-Vote** dataset.

Current loaded dataset:

| Metric            |   Value |
| ----------------- | ------: |
| Nodes             |   7,115 |
| Relationships     | 103,689 |
| Relationship type | `VOTED` |
| Node label        |  `User` |

## Environment

* Python 3.10
* Neo4j Python Driver 6.2.0
* pandas
* NumPy
* CognoDB Cloud
* Windows / PowerShell

## Project Structure

```text
cognodb-cloud-benchmark/
â”‚
â”œâ”€â”€ data/
â”‚   â””â”€â”€ Wiki-Vote.txt
â”‚
â”œâ”€â”€ docs/
â”‚
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ benchmark.py
â”‚   â”œâ”€â”€ 3hop_benchmark.py
â”‚   â”œâ”€â”€ check_cognodb.py
â”‚   â”œâ”€â”€ clear_cognodb.py
â”‚   â”œâ”€â”€ connect.py
â”‚   â”œâ”€â”€ dataset.py
â”‚   â”œâ”€â”€ load_cognodb.py
â”‚   â”œâ”€â”€ load_test.py
â”‚   â”œâ”€â”€ lookup_benchmark.py
â”‚   â””â”€â”€ traversal_benchmark.py
â”‚
â”œâ”€â”€ .env
â”œâ”€â”€ .gitignore
â”œâ”€â”€ requirements.txt
â”œâ”€â”€ README.md
â””â”€â”€ benchmark_results.csv
```

## Installation

Clone the repository and enter the project directory.

Install the required Python packages:

```powershell
python -m pip install -r requirements.txt
```

The required packages include:

* `neo4j`
* `pandas`
* `numpy`

## Configuration

Create a `.env` file in the project root.

The database credentials are kept outside the source code.

Example:

```text
COGNODB_URI=<your-cognodb-bolt-uri>
COGNODB_USERNAME=<your-username>
COGNODB_PASSWORD=<your-password>
```

Do not commit `.env` or database credentials to Git.

## Database Connection Test

Run:

```powershell
python src/connect.py
```

A successful connection should produce output similar to:

```text
CognoDB connection successful!
Test query result: 1
```

## Dataset Loading

The full Wiki-Vote dataset can be loaded into CognoDB using:

```powershell
python src/load_cognodb.py
```

The completed full load produced:

```text
Nodes discovered: 7115
Relationships processed: 103689
Load time: 405.082 seconds
Relationships/sec: 255.97
```

## Verify Data

Run:

```powershell
python src/check_cognodb.py
```

Expected node count:

```text
Users currently loaded: 7115
```

## Test Load

A smaller test workload can be executed using:

```powershell
python src/load_test.py
```

The test workload attempts 1,000 relationships.

## Traversal Benchmark

Run the 1-hop and 2-hop traversal benchmark:

```powershell
python src/traversal_benchmark.py
```

The benchmark uses warm-up iterations followed by measured iterations.

### 1-Hop Results

| Metric  |     Result |
| ------- | ---------: |
| p50     | 273.497 ms |
| p95     | 279.897 ms |
| Mean    | 274.479 ms |
| Minimum | 271.711 ms |
| Maximum | 304.852 ms |
| Samples |        100 |

### 2-Hop Results

| Metric  |     Result |
| ------- | ---------: |
| p50     | 274.266 ms |
| p95     | 297.278 ms |
| Mean    | 278.025 ms |
| Minimum | 271.537 ms |
| Maximum | 350.004 ms |
| Samples |        100 |

## 3-Hop Benchmark

Run:

```powershell
python src/3hop_benchmark.py
```

A successful 20-sample run produced:

| Metric  |      Result |
| ------- | ----------: |
| p50     |  322.298 ms |
| p95     | 1357.704 ms |
| Mean    |  604.679 ms |
| Minimum |  273.324 ms |
| Maximum | 2632.178 ms |
| Samples |          20 |

The 3-hop workload showed substantially higher tail latency than the 1-hop and 2-hop workloads.

The large difference between p50 and p95 indicates that some graph traversals can become significantly more expensive depending on the starting node and traversal fan-out.

## 1,000 Operation Benchmark

Run:

```powershell
python src/benchmark.py
```

A recent benchmark run produced:

```text
Operations: 1000
Execution time: 282.699 seconds
Average latency: 282.699 ms
Operations/sec: 3.54
```

An earlier run produced:

```text
Operations: 1000
Execution time: 264.314 seconds
Average latency: 264.314 ms
Operations/sec: 3.78
```

The difference between runs demonstrates normal variability in cloud database latency.

## Performance Summary

| Workload                   |               Key Result |
| -------------------------- | -----------------------: |
| Full dataset load          |              405.082 sec |
| Load throughput            | 255.97 relationships/sec |
| 1-hop p50                  |               273.497 ms |
| 2-hop p50                  |               274.266 ms |
| 3-hop p50                  |               322.298 ms |
| 3-hop p95                  |              1357.704 ms |
| 1,000-operation throughput |             3.54 ops/sec |

## Observations

### Dataset Loading

The full dataset contains 7,115 users and 103,689 relationships. The database successfully loaded the complete graph.

### 1-Hop vs 2-Hop

The measured p50 latency for 1-hop and 2-hop traversals was very similar:

* 1-hop: 273.497 ms
* 2-hop: 274.266 ms

This indicates that the additional traversal depth did not significantly increase median latency for these workloads.

### 3-Hop Traversal

The 3-hop benchmark showed a higher median latency and substantially higher tail latency.

The p95 latency was approximately 1.36 seconds, while the maximum observed latency was approximately 2.63 seconds.

This suggests that graph fan-out and traversal complexity can have a significant impact on individual query latency.

### Cloud Variability

The 1,000-operation benchmark produced:

* 3.78 ops/sec in one run
* 3.54 ops/sec in another run

Cloud database workloads can vary between runs because of network conditions, database load, caching, and resource scheduling.

## Reproducibility

A typical benchmark workflow is:

```powershell
python -m pip install -r requirements.txt
python src/connect.py
python src/load_cognodb.py
python src/check_cognodb.py
python src/traversal_benchmark.py
python src/3hop_benchmark.py
python src/benchmark.py
```

The benchmark uses deterministic random selection where applicable, including a fixed random seed for traversal workloads.

## Security

Database credentials are stored in `.env`.

The `.env` file is excluded from Git using `.gitignore`.

The Wiki-Vote dataset and generated benchmark results are also excluded from version control where appropriate.

## Conclusion

This benchmark demonstrates a working CognoDB Cloud graph workload using a Neo4j-compatible Python driver.

The database successfully handled:

* Full Wiki-Vote dataset loading
* More than 100,000 graph relationships
* Multi-hop graph traversals
* Repeated benchmark workloads

Median traversal latency remained around the 270â€“320 ms range for the tested workloads, while deeper 3-hop traversals showed significantly higher tail latency.

The benchmark provides a reproducible baseline for further performance optimization and comparison.

