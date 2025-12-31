import csv
import json

def csv_to_json(csv_file_path, json_file_path):
    # Initialize the JSON structure
    json_data = {}
    
    # Read the CSV file
    with open(csv_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        
        for row in csv_reader:
            # Create the entry for each location
            location_id = row['code']
            json_data[location_id] = {
                'name': row['name'],
                'latlng': [float(row['lat']), float(row['lng'])],
                'description': f"Located on floor {row['floor']}",
                'floor': row['floor']
            }
    
    # Write the JSON data to a file
    with open(json_file_path, mode='w') as json_file:
        json.dump(json_data, json_file, indent=2)
    
    return json_data

# Example usage:
csv_to_json('nodes.csv', 'nodes.json')