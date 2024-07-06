import json

# Load the JSON data from the files
with open('craftables.json', 'r') as f:
    craftables = json.load(f)

with open('primitives.json', 'r') as f:
    primitives = json.load(f)

# Extract the titles from the primitives
primitive_titles = {item['title'] for item in primitives}

# Filter out items that have titles in the primitive titles
filtered_items = [item for item in craftables if item['title'] not in primitive_titles]

# Save the filtered items to craftables.json
with open('craftables.json', 'w') as f:
    json.dump(filtered_items, f, indent=4)

print("Filtered items saved to craftables.json")
