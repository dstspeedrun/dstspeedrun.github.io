import json

# Load the JSON data from craftables.json
with open('craftables.json', 'r') as f:
    craftables = json.load(f)

# Initialize a list to hold updated items
updated_craftables = []

# Process each item in craftables
for item in craftables:
    if item['title'] == 'Books':
        # Update titles for items with title "Books" based on URL
        url_parts = item['url'].split('#')
        if len(url_parts) > 1:
            new_title = url_parts[-1].replace('_', ' ')
            item['title'] = new_title

            if new_title == 'The End is Nigh':
                item['title'] = 'The End is Nigh!'
    elif item['title'] == 'Bernie':
        item['title'] = 'Bernie (item)'
    elif item['title'] in ['Hammer', "Relic"]:
        item['url'] = item['url'] + '/DST'
    elif item['title'] == 'Pillar Scaffold':
        item['title'] = "Reinforced Pillar"
    elif item['title'] in ['Round Wooden Table', 'Square Wooden Table']:
        item['title'] = "Square/Round Wooden Table"
    elif item['title'] == 'Wooden Stool':
        item['title'] = "Wooden Chair"

    # Append the updated or unchanged item to the list
    updated_craftables.append(item)

# Save the updated craftables.json
with open('craftables.json', 'w') as f:
    json.dump(updated_craftables, f, indent=4)

print("Updated titles/links in craftables.json")