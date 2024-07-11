import json
import math

def resolve_crafting(items):
    # Create a dictionary to quickly lookup items by title
    item_dict = {item['title']: item for item in items}

    # Function to recursively resolve ingredients
    def resolve_hammerables(item, item_dict):
        resolved_crafting = {}
        if 'crafting' in item:
            for ingredient, count in item['crafting'].items():
                if ingredient in item_dict:
                    sub_item = item_dict[ingredient]
                    sub_crafting = resolve_hammerables(sub_item, item_dict)
                    # Aggregate counts of ingredients at each level
                    for k, v in sub_crafting.items():
                        resolved_crafting[k] = resolved_crafting.get(k, 0) + v * count
                else:
                    # If ingredient not found in item_dict, add it directly
                    resolved_crafting[ingredient] = count
        return resolved_crafting

    # Resolve crafting for each item
    for item in items:
        if 'crafting' in item:
            resolved_crafting = resolve_hammerables(item, item_dict)
            # Update the original item with resolved crafting
            item['crafting'] = resolved_crafting

    return items

# Read from "updated_craftables.json"
with open('craftables.json', 'r') as f:
    items = json.load(f)

# Update ingredient values
for item in items:
    # Create a list of ingredients to be removed
    ingredients_to_remove = []
    
    if 'crafting' in item and item['hammerable']:
        for ingredient_name, ingredient_data in item['crafting'].items():
            # Divide the ingredient value by half
            new_value = ingredient_data / 2
            
            # If result is less than 1, mark ingredient for removal, else ceil it to the next integer
            if new_value < 1:
                ingredients_to_remove.append(ingredient_name)
            else:
                item['crafting'][ingredient_name] = math.floor(new_value)
    
    # Remove marked ingredients from the crafting list
    for ingredient_name in ingredients_to_remove:
        del item['crafting'][ingredient_name]

# Resolve crafting ingredients
resolved_items = resolve_crafting(items)

# Save to a JSON file
with open('hammerables.json', 'w') as f:
    json.dump(resolved_items, f, indent=4)

print("Resolved items saved to hammerables.json")