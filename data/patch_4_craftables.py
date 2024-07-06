import json

# Load the JSON data from craftables.json
with open('craftables.json', 'r') as f:
    craftables = json.load(f)

# Initialize a dictionary to track unique items based on title and url
unique_items = {}

# Identify and keep only unique items based on title and url
for item in craftables:
    key = (item['title'], item['url'])
    if key not in unique_items:
        unique_items[key] = item

# Convert dictionary values (unique items) back to a list
updated_craftables = list(unique_items.values())

# Save the updated craftables.json without duplicates
with open('craftables.json', 'w') as f:
    json.dump(updated_craftables, f, indent=4)

print("Duplicate items removed from craftables.json based on title and url.")
