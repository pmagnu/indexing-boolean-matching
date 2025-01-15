import urllib.parse
import urllib.robotparser
import urllib.request
from urllib.error import HTTPError

class CrawlQueueManager:
    def __init__(self):
        self.urls_to_crawl = []
        self.visited_urls = set()
        self.robots_cache = {}  # Cache for robots.txt rules
    
    def add_url(self, url):
        if url not in self.visited_urls and self.is_crawl_allowed(url):
            self.urls_to_crawl.append(url)

    def get_next_url(self):
        if self.urls_to_crawl:
            return self.urls_to_crawl.pop(0)

    def mark_visited(self, url):
        self.visited_urls.add(url)

    def is_visited(self, url):
        return url in self.visited_urls
    
    def is_crawl_allowed(self, url, user_agent='MyCrawler', timeout=10):
        # Parse the base URL to extract the scheme and network location (domain)
        parsed_url = urllib.parse.urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # Check if we've already fetched robots.txt for this domain
        if base_url in self.robots_cache:
            rp = self.robots_cache[base_url]
        else:
            rp = urllib.robotparser.RobotFileParser()
            robots_url = f"{base_url}/robots.txt"

            try:
                # Fetch robots.txt with a timeout
                with urllib.request.urlopen(robots_url, timeout=timeout) as response:
                    rp.parse(response.read().decode('utf-8').splitlines())
                    print(f"Parsed robots.txt for {base_url}")
            except HTTPError as e:
                if e.code == 404:
                    # If robots.txt is not found, assume unrestricted access
                    print(f'robots.txt not found for {base_url}: Assuming unrestricted access.')
                    rp.allow_all = True
                elif e.code == 403:
                    # If access is forbidden, assume crawling is not allowed
                    print(f'Access to robots.txt forbidden for {base_url}: Assuming crawling disallowed.')
                    rp.allow_none = True
                else:
                    print(f'Error fetching robots.txt for {base_url}: HTTP Error {e.code}')
                    rp.allow_none = True
            except Exception as e:
                print(f'Error fetching robots.txt for {base_url}: {e}')
                rp.allow_none = True

            # Cache the parsed rules for the domain
            self.robots_cache[base_url] = rp
        
        # Check if crawling is allowed
        return rp.can_fetch(user_agent, url)
    
    def has_urls_to_crawl(self):
        return len(self.urls_to_crawl) > 0
