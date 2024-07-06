import json

# Load the JSON data from the files
with open('craftables.json', 'r') as f:
    craftables = json.load(f)

with open('primitives.json', 'r') as f:
    primitives = json.load(f)

# Define the titles to move
titles_to_move = {"Meat", "Morsel"}

# Initialize a list to hold items to move
items_to_move = []

# Filter out items to move and update primitives
updated_primitives = primitives.copy()

for item in craftables:
    if item['title'] in titles_to_move:
        items_to_move.append(item)
        updated_primitives.append(item)

# Save the updated primitives to primitives.json
with open('primitives.json', 'w') as f:
    json.dump(updated_primitives, f, indent=4)

# Remove the items from craftables.json that were moved
updated_craftables = [item for item in craftables if item['title'] not in titles_to_move]

# Save the updated craftables.json
with open('craftables.json', 'w') as f:
    json.dump(updated_craftables, f, indent=4)

print(f"Moved {len(items_to_move)} items to primitives.json")
