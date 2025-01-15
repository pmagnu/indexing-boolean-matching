import os
import json
import hashlib
from bs4 import BeautifulSoup

class FileContentStorage:
    def __init__(self, storage_dir='crawled_content'):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def save_content(self, url, html_content):
        # Extract title using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        title = soup.title.string if soup.title else 'No Title'
        
        # Extract text content
        text_content = self._extract_text(soup)
        
        # Create a dictionary to store the data
        data = {
            'url': url,
            'title': title,
            'content': text_content
        }
        
        # Create a file-safe name for storing the JSON
        file_name = self._get_file_name(url)
        file_path = os.path.join(self.storage_dir, file_name)
        
        # Save the data as a JSON file
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        
        print(f"Saved content for URL: {url} in {file_path}")

    def _get_file_name(self, url):
        # Use a hash of the URL for unique, safe file names
        return hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'
    
    def _extract_text(self, soup):
        # Extract text content while removing unnecessary tags
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()
        
        text = soup.get_text(separator=' ', strip=True)
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        cleaned_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return cleaned_text

