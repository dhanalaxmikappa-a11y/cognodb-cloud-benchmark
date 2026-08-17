\# CognoDB Cloud Benchmark



Benchmark project for evaluating graph loading and traversal performance on CognoDB Cloud using the Wiki-Vote dataset.



\## Dataset



Dataset: Wiki-Vote



\- Nodes: 7,115

\- Relationships: 103,689

\- Self-loops: 0

\- Unique relationships: 103,689



\## Environment



\- Python: 3.10

\- Neo4j Python Driver: 6.2.0

\- Database: CognoDB Cloud

\- Dataset file: `data/Wiki-Vote.txt`



\## Project Structure



```text

cognodb-cloud-benchmark/

├── data/

│   └── Wiki-Vote.txt

├── docs/

├── src/

│   ├── benchmark.py

│   ├── check\_cognodb.py

│   ├── clear\_cognodb.py

│   ├── config.py

│   ├── connect.py

│   ├── dataset.py

│   ├── load\_cognodb.py

│   ├── load\_test.py

│   └── 3hop\_benchmark.py

├── .env

├── .gitignore

├── benchmark\_results.csv

├── requirements.txt

└── README.md

