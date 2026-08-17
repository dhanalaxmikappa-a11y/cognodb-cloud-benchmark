# CognoDB Cloud Benchmark

A Python-based benchmark project for evaluating graph database loading, traversal, lookup, aggregation, and mixed read/write performance.

The project uses the **Wiki-Vote** graph dataset and compares **CognoDB Cloud** with **Neo4j** using the same dataset and benchmark workloads.

## Overview

This project evaluates graph database performance using:

* Dataset loading
* 3-hop graph traversal
* Point lookup
* Indexed lookup
* Aggregation
* Mixed read/write workload

The same Wiki-Vote dataset was loaded into both databases.

## Dataset

The benchmark uses the **Wiki-Vote** dataset.

| Metric            |   Value |
| ----------------- | ------: |
| Nodes             |   7,115 |
| Relationships     | 103,689 |
| Relationship type | `VOTED` |
| Node label        |  `User` |

## Environment

* Windows / PowerShell
* Python 3.10.11
* Neo4j Python Driver
* pandas
* NumPy
* CognoDB Cloud
* Neo4j Cloud

## Project Structure

```text
cognodb-cloud-benchmark/
│
├── data/
│   └── Wiki-Vote.txt
│
├── docs/
│
├── src/
│   ├── 3hop_benchmark.py
│   ├── aggregation_benchmark.py
│   ├── indexed_lookup_benchmark.py
│   ├── mixed_workload.py
│   │
│   ├── neo4j_traversal_benchmark.py
│   ├── neo4j_lookup_benchmark.py
│   ├── neo4j_indexed_lookup_benchmark.py
│   ├── neo4j_aggregation_benchmark.py
│   ├── neo4j_mixed_workload.py
│   └── load_neo4j.py
│
├── .env
├── .gitignore
├── requirements.txt
├── benchmark_results.csv
└── README.md
```

## Installation

Install the required Python packages:

```powershell
python -m pip install -r requirements.txt
```

## Configuration

Database credentials are stored in `.env`.

Example:

```text
COGNODB_URI=<your-cognodb-bolt-uri>
COGNODB_USERNAME=<your-username>
COGNODB_PASSWORD=<your-password>

NEO4J_URI=<your-neo4j-uri>
NEO4J_USERNAME=<your-username>
NEO4J_PASSWORD=<your-password>
NEO4J_DATABASE=<your-database>
```

Do not commit `.env` or database credentials to Git.

---

# CognoDB Results

## Dataset Loading

The Wiki-Vote dataset was successfully loaded into CognoDB.

Dataset size:

* Nodes: **7,115**
* Relationships: **103,689**

## 3-Hop Traversal

A 100-sample benchmark was executed after warm-up iterations.

| Metric  |       Result |
| ------- | -----------: |
| p50     |   307.454 ms |
| p95     | 1,365.739 ms |
| Mean    |   468.050 ms |
| Minimum |   269.531 ms |
| Maximum | 2,635.521 ms |
| Samples |          100 |

## Aggregation

| Metric  |     Result |
| ------- | ---------: |
| p50     | 307.064 ms |
| p95     | 357.629 ms |
| Mean    | 312.322 ms |
| Minimum | 281.159 ms |
| Maximum | 791.724 ms |
| Samples |        100 |

Users counted: **7,115**

## Indexed Point Lookup

A `User.id` range index was created and verified before the benchmark.

Index:

```text
user_id_index
Label: User
Property: id
Type: RANGE
State: ONLINE
```

| Metric  |     Result |
| ------- | ---------: |
| p50     | 307.197 ms |
| p95     | 341.566 ms |
| Mean    | 306.156 ms |
| Minimum | 271.074 ms |
| Maximum | 376.909 ms |
| Samples |        100 |

## Mixed Read/Write Workload

Configuration:

* Concurrency: 10
* Duration: 30 seconds
* Reads: 80%
* Writes: 20%

| Metric                |        Result |
| --------------------- | ------------: |
| Successful operations |           934 |
| Failed operations     |             0 |
| Throughput            | 31.02 ops/sec |
| Average latency       |    321.338 ms |
| Minimum latency       |    261.825 ms |
| Maximum latency       |  3,673.694 ms |

---

# Neo4j Results

The same dataset was loaded into Neo4j.

## Dataset Loading

| Metric                  |                     Result |
| ----------------------- | -------------------------: |
| Nodes                   |                      7,115 |
| Relationships           |                    103,689 |
| Load time               |             12.025 seconds |
| Relationship throughput | 8,622.73 relationships/sec |

## 3-Hop Traversal

100 samples were measured after warm-up.

| Metric  |     Result |
| ------- | ---------: |
| p50     |  55.080 ms |
| p95     |  65.798 ms |
| Mean    |  59.830 ms |
| Minimum |  52.945 ms |
| Maximum | 373.381 ms |
| Samples |        100 |

## Point Lookup

| Metric  |    Result |
| ------- | --------: |
| p50     | 51.278 ms |
| p95     | 54.632 ms |
| Mean    | 51.665 ms |
| Minimum | 49.743 ms |
| Maximum | 60.541 ms |
| Samples |       100 |

## Indexed Point Lookup

The Neo4j `User.id` index was verified as online before testing.

| Metric  |    Result |
| ------- | --------: |
| p50     | 52.920 ms |
| p95     | 56.082 ms |
| Mean    | 53.407 ms |
| Minimum | 51.383 ms |
| Maximum | 69.224 ms |
| Samples |       100 |

## Aggregation

| Metric  |    Result |
| ------- | --------: |
| p50     | 49.785 ms |
| p95     | 53.217 ms |
| Mean    | 50.251 ms |
| Minimum | 48.665 ms |
| Maximum | 59.490 ms |
| Samples |       100 |

Users counted: **7,115**

## Mixed Read/Write Workload

Configuration:

* Concurrency: 10
* Duration: 30 seconds
* Reads: 80%
* Writes: 20%

| Metric                |         Result |
| --------------------- | -------------: |
| Successful operations |          5,121 |
| Failed operations     |              0 |
| Throughput            | 170.30 ops/sec |
| Average latency       |      58.627 ms |
| Minimum latency       |      49.876 ms |
| Maximum latency       |     369.238 ms |

---

# Performance Comparison

The following table compares the final measured results from the two databases.

| Workload           |       CognoDB |              Neo4j |
| ------------------ | ------------: | -----------------: |
| 3-hop p50          |    307.454 ms |      **55.080 ms** |
| 3-hop p95          |  1,365.739 ms |      **65.798 ms** |
| Point lookup p50   |       ~307 ms |      **51.278 ms** |
| Indexed lookup p50 |    307.197 ms |      **52.920 ms** |
| Aggregation p50    |    307.064 ms |      **49.785 ms** |
| Mixed throughput   | 31.02 ops/sec | **170.30 ops/sec** |

## Observations

### Graph Traversal

Neo4j produced substantially lower latency for the tested 3-hop traversal workload.

The measured p50 was approximately:

* CognoDB: **307.454 ms**
* Neo4j: **55.080 ms**

The p95 values were:

* CognoDB: **1,365.739 ms**
* Neo4j: **65.798 ms**

This indicates significantly lower median and tail latency for Neo4j under this workload.

### Point Lookup

Neo4j also showed substantially lower point-lookup latency.

The measured p50 was approximately:

* CognoDB: **307 ms**
* Neo4j: **51.278 ms**

### Indexed Lookup

Both databases were tested with a `User.id` index.

Neo4j produced a p50 of **52.920 ms**, while the CognoDB benchmark produced approximately **307.197 ms**.

### Aggregation

The aggregation benchmark counted the same **7,115 users**.

Measured p50:

* CognoDB: **307.064 ms**
* Neo4j: **49.785 ms**

### Mixed Workload

Both databases were tested using:

* 10 concurrent workers
* 30-second duration
* 80% reads
* 20% writes

Neo4j achieved:

**170.30 ops/sec**

CognoDB achieved:

**31.02 ops/sec**

Both tests reported **0 failed operations**.

---

# Methodology

The benchmarks use warm-up iterations before measured iterations to reduce the effect of initial connection and cache setup.

Unless otherwise specified:

* Warm-up iterations: 20
* Measured iterations: 100
* Random seed: 42 where applicable

The same Wiki-Vote dataset was used for both databases.

The benchmark results represent measurements from the tested cloud environments and should not be interpreted as universal performance guarantees.

Cloud latency can vary because of:

* Network conditions
* Database load
* Resource scheduling
* Caching
* Region and infrastructure differences

## Important Comparison Note

The CognoDB and Neo4j instances were cloud services and may have different infrastructure, resource allocations, regions, and network paths.

Therefore, these results should be interpreted as **observed benchmark results under the tested configurations**, rather than as a controlled hardware-identical comparison.

---

# Reproducibility

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Check CognoDB:

```powershell
python src/check_cognodb.py
```

Run CognoDB benchmarks:

```powershell
python src/3hop_benchmark.py
python src/indexed_lookup_benchmark.py
python src/aggregation_benchmark.py
python src/mixed_workload.py
```

Load the dataset into Neo4j:

```powershell
python src/load_neo4j.py
```

Run Neo4j benchmarks:

```powershell
python src/neo4j_traversal_benchmark.py
python src/neo4j_lookup_benchmark.py
python src/neo4j_indexed_lookup_benchmark.py
python src/neo4j_aggregation_benchmark.py
python src/neo4j_mixed_workload.py
```

---

# Security

Database credentials must remain in `.env`.

The `.env` file should be excluded using `.gitignore`.

Never publish:

* Database passwords
* API keys
* Private connection strings containing credentials
* Authentication tokens

---

# Conclusion

This project establishes a reproducible graph database benchmark using the Wiki-Vote dataset with **7,115 nodes and 103,689 relationships**.

The completed experiments cover:

* Dataset loading
* Multi-hop graph traversal
* Point lookup
* Indexed lookup
* Aggregation
* Mixed read/write workloads

Under the tested configurations, Neo4j produced lower latency and higher mixed-workload throughput than CognoDB.

The project can be extended by adding additional graph database systems using the same dataset and workload definitions.
