from pathlib import Path


DATASET_FILE = Path("data/Wiki-Vote.txt")


def analyze_dataset():
    nodes = set()
    edges = 0
    self_loops = 0
    unique_edges = set()

    with DATASET_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            source, target = map(int, line.split())

            nodes.add(source)
            nodes.add(target)

            edges += 1
            unique_edges.add((source, target))

            if source == target:
                self_loops += 1

    return {
        "nodes": len(nodes),
        "relationships": edges,
        "unique_relationships": len(unique_edges),
        "self_loops": self_loops,
    }


def main():
    result = analyze_dataset()

    print("Wiki-Vote Dataset")
    print("=" * 30)
    print(f"Nodes: {result['nodes']}")
    print(f"Relationships: {result['relationships']}")
    print(f"Unique relationships: {result['unique_relationships']}")
    print(f"Self-loops: {result['self_loops']}")


if __name__ == "__main__":
    main()