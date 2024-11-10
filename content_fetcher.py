import requests
from bs4 import BeautifulSoup

class ContentFetcher:
    def __init__(self, url: str):
        self.url = url

    def fetch_content(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            plain_text = soup.get_text(separator=' ', strip=True)
            
            return plain_text
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching content from {self.url}: {e}")
            return None
