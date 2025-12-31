import csv
import math


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    Returns distance in meters
    """
    # Earth radius in meters
    R = 6371e3

    # Convert degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# Read nodes into a dictionary for quick lookup
nodes = {}
with open("nodes.csv", mode="r") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        nodes[row["code"]] = {"lat": float(row["lat"]), "lng": float(row["lng"])}

# Read edges and update distances
updated_edges = []
missing_count = 0
missing_codes = set()  # Track all missing node codes

with open("edges.csv", mode="r") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        from_node = row["from"]
        to_node = row["to"]

        # Check if both nodes exist
        if from_node in nodes and to_node in nodes:
            from_data = nodes[from_node]
            to_data = nodes[to_node]

            distance = haversine_distance(
                from_data["lat"], from_data["lng"], to_data["lat"], to_data["lng"]
            )
            row["distance"] = round(distance, 2)
        else:
            # Set distance to 0 for missing nodes
            row["distance"] = 0
            missing_count += 1

            # Track missing codes
            if from_node not in nodes:
                missing_codes.add(from_node)
            if to_node not in nodes:
                missing_codes.add(to_node)

        updated_edges.append(row)

# Write updated edges back to file
with open("edges.csv", mode="w", newline="") as csvfile:
    fieldnames = ["from", "to", "distance"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(updated_edges)

# Print summary and missing codes
print(f"Processing complete!")
print(f"- Updated distances for {len(updated_edges) - missing_count} edges")
print(f"- Set {missing_count} edges to 0 (missing nodes)")
print("\nMissing node codes:")
for code in sorted(missing_codes):
    print(f"  - {code}")
