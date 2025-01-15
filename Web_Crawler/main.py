import urllib.parse
import urllib.robotparser
import urllib.request
from bs4 import BeautifulSoup
from time import sleep

from Web_Crawler.StorageManagement import FileContentStorage
from Web_Crawler.CrawlQueueManager import CrawlQueueManager

def crawl_website(seed_url):
    queue_manager = CrawlQueueManager()
    queue_manager.add_url(seed_url)
    storage = FileContentStorage()

    count = 0
    while count < 1000:
        current_url = queue_manager.get_next_url()

        if queue_manager.is_visited(current_url):
            continue

        if not queue_manager.is_crawl_allowed(current_url):
            print(f"Crawling disallowed by robots.txt: {current_url}")
            continue

        sleep(3)  # Respect robots.txt crawl delay before making the request

        print(f'Starting to crawl: {current_url}')
        html_content = get_html_content(current_url)

        if html_content:
            # Save the HTML content as a JSON file
            storage.save_content(current_url, html_content)

            links = extract_link_from_html(current_url, html_content)
            print(f'Found {len(links)} links')

            for link in links:
                queue_manager.add_url(link)
                
        queue_manager.mark_visited(current_url)
        count += 1

    print('Crawling has ended')

def get_html_content(url):
    try:
        with urllib.request.urlopen(url) as response:
            return response.read()
    except Exception as e:
        print(f'Error fetching HTML content from {url}: {e}')
        return None

def extract_link_from_html(base_url, html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    unique_links = set()

    for anchor_tag in soup.find_all('a', href=True):
        href = anchor_tag.get('href')
        full_url = urllib.parse.urljoin(base_url, href)
        unique_links.add(full_url)

    return unique_links

def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    text = soup.get_text(separator=' ', strip=True)

    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    cleaned_text = '\n'.join(chunk for chunk in chunks if chunk)

    return cleaned_text


#####################

seed_url = "https://kvf.fo/"
crawl_website(seed_url)