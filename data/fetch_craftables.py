import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

# URL of the page to scrape
url = "https://dontstarve.wiki.gg/wiki/Template:Craftable_Items_and_Structures_on_DST"

try:
    # Fetching the page content
    response = requests.get(url)
    response.raise_for_status()  # Raise error for bad responses
    soup = BeautifulSoup(response.text, 'html.parser')

    # Finding the table with specific class
    table = soup.find('table', class_='navbox')

    # Deleting all td tags with class "navbox-group"
    if table:
        table.find('a', {'title':"Special Event Filter"}, string='Special Event').parent.parent.parent.decompose()
        table.find('a', {'title':"Critters Filter"}, string='Critters').parent.parent.parent.decompose()
        table.find('a', {'title':"Bottle Exchange Filter"}, string='Bottle Exchange').parent.parent.parent.decompose()
        table.find('a', {'title':"Sculptures Filter"}, string='Sculptures').parent.parent.parent.decompose()
        table.find('a', {'title':"Offerings Filter"}, string='Offerings').parent.parent.parent.decompose()
        table.find('a', {'title':"Cawnival Creation Filter"}, string='Cawnival Creation').parent.parent.parent.decompose()
        table.find('a', {'title':"Mad Science Filter"}, string='Mad Science').parent.parent.parent.decompose()
        table.find('a', {'title':"Trinket Trove Filter"}, string='Trinket Trove').parent.parent.parent.decompose()
        table.find('a', {'title':"Winter's Feast Cooking Filter"}, string="Winter's Feast Cooking").parent.parent.parent.decompose()
        for td in table.find_all('td', class_='navbox-group'):
            td.decompose()
        table.find('article', {'data-mw-tabber-title': 'Wilson'}, class_='tabber__panel').decompose()


    # Extracting information from <a> tags
    items = []
    if table:
        for a in table.find_all('a'):
            try:
                href = a.get('href')
                if href:
                    href = urljoin(url, href.strip())
                title = a.get('title', '').strip().split('/')[0]
                img_src = a.find('img').get('src')
                if img_src:
                    img_src = urljoin(url, img_src.strip())

                item_data = {
                    'title': title,
                    'url': href,
                    'image_url': img_src
                }
                items.append(item_data)
            except AttributeError:
                # Handle cases where <a> tag does not have expected attributes
                continue

    # Saving the extracted data to JSON file
    with open('craftables.json', 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=4)

    print(f"Successfully saved {len(items)} items to craftables.json.")

except requests.exceptions.RequestException as e:
    print(f"Error fetching page: {e}")
except Exception as e:
    print(f"An error occurred: {e}")