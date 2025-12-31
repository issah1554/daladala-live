import csv
from collections import defaultdict
import json


def convert_edges_to_graph(csv_file):
    graph = defaultdict(dict)

    with open(csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            from_node = row["from"]
            to_node = row["to"]

            try:
                # First try converting directly to float (handles decimals)
                distance = float(row["distance"])
                # Then convert to int if it's a whole number for cleaner output
                distance = int(distance) if distance.is_integer() else distance
            except (ValueError, TypeError):
                # Handle missing/empty/invalid values (set to 0 or other default)
                distance = 0  # Or use None if you prefer

            # Add both directions (assuming bidirectional paths)
            graph[from_node][to_node] = distance
            graph[to_node][from_node] = distance

    return dict(graph)


def save_as_json(graph, output_file):
    with open(output_file, "w") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    graph = convert_edges_to_graph("edges.csv")
    save_as_json(graph, "graph.json")
    print("Successfully generated graph.json")
