import json

# Load the JSON data from primitives.json
with open('primitives.json', 'r') as f:
    primitives = json.load(f)

# Initialize a dictionary to track unique items based on title and url
unique_items = {}

# Identify and keep only unique items based on title and url
for item in primitives:
    key = (item['title'])
    if key not in unique_items:
        unique_items[key] = item

# Convert dictionary values (unique items) back to a list
updated_primitives = list(unique_items.values())

# Save the updated primitives.json without duplicates
with open('primitives.json', 'w') as f:
    json.dump(updated_primitives, f, indent=4)

print("Duplicate items removed from primitives.json based on title only.")
