import json
import re
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from tqdm.asyncio import tqdm
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

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

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(aiohttp.ClientError))
async def fetch_page(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

async def fetch_item_data(item, session, progress_bar):
    url = item['url']
    title = item['title']

    response_text = await fetch_page(session, url)
    if not response_text:
        progress_bar.update(1)
        return

    soup = BeautifulSoup(response_text, 'html.parser')

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

            hammerable = soup.find('div', {'data-source': 'tool'})
            if hammerable and 'Hammer' in str(hammerable):
                item['hammerable'] = True
            else:
                item['hammerable'] = False

            progress_bar.update(1)
            return
        item['hammerable'] = False
    # Update progress bar after task completion
    progress_bar.update(1)

async def fetch_all_items(craftables):
    async with aiohttp.ClientSession() as session:
        with tqdm(total=len(craftables), desc="Processing items") as pbar:
            tasks = [fetch_item_data(item, session, pbar) for item in craftables]
            await asyncio.gather(*tasks)

# Load craftables.json
with open('craftables.json', 'r', encoding='utf-8') as f:
    craftables = json.load(f)

# Fetch all items
asyncio.run(fetch_all_items(craftables))

# Save the updated data to a new JSON file
with open('updated_craftables.json', 'w', encoding='utf-8') as f:
    json.dump(craftables, f, ensure_ascii=False, indent=4)

print(f"Successfully updated {len(craftables)} items and saved to updated_craftables.json.")