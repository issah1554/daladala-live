import json

INPUT_FILE = "morogoro-road.json"
OUTPUT_FILE = "morogoro-road-linestring.json"

coords = []

with open(INPUT_FILE, "r") as f:
    data = json.load(f)

for element in data.get("elements", []):
    if element.get("type") == "way" and "geometry" in element:
        for point in element["geometry"]:
            lon = point["lon"]
            lat = point["lat"]
            coords.append(f"{lon} {lat}")

linestring = f"LINESTRING({', '.join(coords)})"

output = {"geometry": linestring}

with open(OUTPUT_FILE, "w") as f:
    json.dump(output, f, indent=2)

print(linestring)
