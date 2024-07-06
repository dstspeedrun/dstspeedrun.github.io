import json
import re
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# Function to extract ingredient data
def extract_ingredients(soup):
    ingredients = {}
    title_pattern = r'title="([^"]*)"[^>]*>'
    amount_pattern = r'>×(\d+)\ \(?'

    div = soup.find('div', {'data-source': 'ingredient1'})
    if div:
        value_div = div.find('div', class_='pi-data-value')
        if value_div:
            # Extract all titles and their associated amounts
            titles = re.findall(title_pattern, str(value_div))
            amounts = re.findall(amount_pattern, str(value_div))
            titles = titles[:len(amounts)]

            amounts = list(map(int, amounts))

            ingredients = {key.split('/')[0]: value for key, value in zip(titles, amounts)}

    return ingredients

# Function to extract crafting text data
def extract_crafting_text(soup):
    crafting_text = {}
    title_pattern = r'title="([^"]*)"[^>]*>'
    amount_pattern = r'>x(\d+)\ ?<'
    div = soup.find('div', {'data-source': 'crafting_text'})
    if div:
        value_div = div.find('div', class_='pi-data-value')
        if value_div:
            # Extract all <p> tags inside the first <article> with class "tabber__panel"
            article = value_div.find('article', class_='tabber__panel')
            if article:
                p = article.find('p')
                if p:
                    # Extract all titles and their associated amounts
                    titles = re.findall(title_pattern, str(p))
                    amounts = re.findall(amount_pattern, str(p))
                    titles = titles[:len(amounts)]

                    amounts = list(map(int, amounts))

                    crafting_text = {key.split('/')[0]: value for key, value in zip(titles, amounts)}

    return crafting_text

def fetch_item_data(item, session, progress_bar):
    url = item['url']
    title = item['title']

    response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the title in the HTML
    h2 = soup.find('h2', class_='pi-item pi-item-spacing pi-title', string=title)

    if h2:
        soup = h2.parent
        # Extract ingredient data
        ingredients = extract_ingredients(soup)

        # Extract crafting text data
        crafting_text = extract_crafting_text(soup)

        # Combine all crafting data
        crafting_data = {**ingredients, **crafting_text}
        if crafting_data:
            item['crafting'] = crafting_data

    # Update progress bar after task completion
    progress_bar.update(1)

def fetch_all_items(craftables):
    with requests.Session() as session:
        # Initialize tqdm progress bar
        with tqdm(total=len(craftables)) as pbar:
            for item in craftables:
                fetch_item_data(item, session, pbar)

# Load craftables.json
with open('craftables.json', 'r', encoding='utf-8') as f:
    craftables = json.load(f)

# Fetch all items
fetch_all_items(craftables)

# Save the updated data to a new JSON file
with open('craftables.json', 'w', encoding='utf-8') as f:
    json.dump(craftables, f, ensure_ascii=False, indent=4)

print(f"Successfully updated {len(craftables)} items and saved to updated_craftables.json.")