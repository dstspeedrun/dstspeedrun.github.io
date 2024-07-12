import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
import asyncio
import aiohttp
from tqdm.asyncio import tqdm
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

# URL of the page to scrape
url = "https://dontstarve.wiki.gg/wiki/Template:Resources"
base_url = "https://dontstarve.wiki.gg"

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(aiohttp.ClientError))
async def fetch_page(session, url):
    try:
        async with session.get(url) as response:
            return await response.text()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

async def check_url_and_update(session, item, pbar):
    full_url = item['url']
    dst_url = f"{full_url}/DST"
    response_text = await fetch_page(session, dst_url)

    if response_text and "There is currently no text in this page." not in response_text:
        item['url'] = dst_url
    
    pbar.update(1)

async def main():
    try:
        # Fetching the page content
        response = requests.get(url)
        response.raise_for_status()  # Raise error for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')

        # Finding the table with specific class
        table = soup.find('table', class_='navbox')

        parent_of_td_tag = table.find('td', class_='navbox-group', recursive=True, string='Craftable Resources').parent
        parent_of_td_tag.decompose()

        # Extracting information from <a> tags
        items = []
        if table:
            for a in table.find_all('a'):
                try:
                    href = a.get('href')
                    if href:
                        full_url = urljoin(base_url, href.strip())

                    title = a.get('title', '').strip().split('/')[0]
                    img_src = a.find('img').get('src')
                    if img_src:
                        img_src = urljoin(base_url, img_src.strip())

                    item_data = {
                        'title': title,
                        'url': full_url,
                        'image_url': img_src
                    }
                    items.append(item_data)
                except AttributeError:
                    # Handle cases where <a> tag does not have expected attributes
                    continue

        # Check each URL and update if the /DST URL is valid
        async with aiohttp.ClientSession() as session:
            with tqdm(total=len(items), desc="Processing items") as pbar:
                tasks = [check_url_and_update(session, item, pbar) for item in items]
                await asyncio.gather(*tasks)

        # Saving the extracted data to JSON file
        with open('primitives.json', 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=4)

        print(f"Successfully saved {len(items)} items to primitives.json.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the main function
asyncio.run(main())