"""
Web Scraper - A professional scraping tool
Author: Abbas Hussain Muzammil
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import time
from typing import List, Dict, Optional


#Setup logging
logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s'

)
logger = logging.getLogger(__name__)

class WebScraper:
    """
    A professional web scraper with error handling and logging.
    """
    
    def __init__(self, base_url: str, delay: float = 1.0):
        """
        Initialize the scraper.
        
        Args:
            base_url: The website to scrape
            delay: Seconds to wait between requests (be nice to servers!)
        """
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        
        # Set a proper user agent (identify ourselves)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Educational Web Scraper)'
        })
        
        logger.info(f"Scraper initialized for {base_url}")

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a web page.
        
        Args:
            url: The URL to fetch
            
        Returns:
            BeautifulSoup object if successful, None if failed
        """
        try:
            logger.info(f"Fetching: {url}")
            
            # Wait to be polite to the server
            time.sleep(self.delay)
            
            # Make the request
            response = self.session.get(url, timeout=15)
            
            # Raise error if status code is bad (404, 500, etc.)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.content, 'lxml')
            
            logger.info(f"Successfully fetched {url}")
            return soup
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None 

    def scrape_quotes(self) -> List[Dict]:
        """
        Scrape quotes from quotes.toscrape.com
        
        Returns:
            List of dictionaries with quote data
        """
        url = "http://quotes.toscrape.com/"
        soup = self.fetch_page(url)
        
        if not soup:
            logger.warning("Failed to fetch page")
            return []
        
        quotes_data = []
        
        # Find all quote elements
        quotes = soup.find_all('div', class_='quote')
        
        for quote in quotes:
            try:
                # Extract the text
                text = quote.find('span', class_='text').get_text(strip=True)
                
                # Extract the author
                author = quote.find('small', class_='author').get_text(strip=True)
                
                # Extract tags
                tags = [tag.get_text(strip=True) for tag in quote.find_all('a', class_='tag')]
                
                quotes_data.append({
                    'quote': text,
                    'author': author,
                    'tags': ', '.join(tags)
                })
                
            except AttributeError as e:
                logger.warning(f"Error parsing quote: {e}")
                continue
        
        logger.info(f"Scraped {len(quotes_data)} quotes")
        return quotes_data
    def scrape_books(self, num_pages: int = 3) -> List[Dict]:
        """
        Scrape books from multiple pages.
        
        Args:
            num_pages: Number of pages to scrape
            
        Returns:
            List of book data
        """
        books_data = []
        base_url = "http://books.toscrape.com/catalogue/page-{}.html"
        
        for page in range(1, num_pages + 1):
            url = base_url.format(page)
            soup = self.fetch_page(url)
            
            if not soup:
                logger.warning(f"Failed to fetch page {page}")
                continue
            
            # Find all book containers
            books = soup.find_all('article', class_='product_pod')
            
            for book in books:
                try:
                    # Extract title
                    title = book.find('h3').find('a')['title']
                    
                    # Extract price
                    price = book.find('p', class_='price_color').get_text(strip=True)
                    price_clean = float(price.replace('£', ''))
                    
                    # Extract rating (One, Two, Three, Four, Five)
                    rating = book.find('p', class_='star-rating')['class'][1]
                    
                    # Extract availability
                    availability = book.find('p', class_='instock availability').get_text(strip=True)
                    
                    books_data.append({
                        'title': title,
                        'price': price_clean,
                        'rating': rating,
                        'availability': availability,
                        'page': page
                    })
                    
                except (AttributeError, ValueError, KeyError) as e:
                    logger.warning(f"Error parsing book: {e}")
                    continue
            
            logger.info(f"Scraped page {page}: {len(books)} books found")
        
        logger.info(f"Total books scraped: {len(books_data)}")
        return books_data

    def save_to_csv(self, data: List[Dict], filename: str) -> None:
        """
        Save scraped data to CSV file.
        
        Args:
            data: List of dictionaries to save
            filename: Name of the output file
        """
        if not data:
            logger.warning("No data to save")
            return
        
        try:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False, encoding='utf-8')
            logger.info(f"✓ Saved {len(df)} records to {filename}")
            
            # Show a preview
            print(f"\nPreview of {filename}:")
            print(df.head())
            
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")       


def main():
    """
    Main function to run the scraper.
    """
    print("=" * 70)
    print("WEB SCRAPER - Professional Version")
    print("=" * 70)
    
    # Example 1: Scrape Quotes
    print("\n📚 Example 1: Scraping Quotes...")
    print("-" * 70)
    scraper = WebScraper("http://quotes.toscrape.com", delay=1.0)
    quotes = scraper.scrape_quotes()
    
    if quotes:
        scraper.save_to_csv(quotes, 'quotes_output.csv')
        print(f"✅ Scraped {len(quotes)} quotes")
    
    # Example 2: Scrape Books (Multiple Pages)
    print("\n📖 Example 2: Scraping Books (3 pages)...")
    print("-" * 70)
    scraper = WebScraper("http://books.toscrape.com", delay=1.0)
    books = scraper.scrape_books(num_pages=3)
    
    if books:
        scraper.save_to_csv(books, 'books_output.csv')
        print(f"✅ Scraped {len(books)} books")
        
        # Show some analysis
        import pandas as pd
        df = pd.DataFrame(books)
        print(f"\n📊 Quick Analysis:")
        print(f"   Average price: £{df['price'].mean():.2f}")
        print(f"   Most expensive: £{df['price'].max():.2f}")
        print(f"   Cheapest: £{df['price'].min():.2f}")
        
        # Show rating distribution
        print(f"\n⭐ Rating distribution:")
        rating_counts = df['rating'].value_counts()
        for rating, count in rating_counts.items():
            print(f"   {rating}: {count} books")
    
    print("\n" + "=" * 70)
    print("✅ ALL DONE! Check your CSV files!")
    print("=" * 70)


if __name__ == "__main__":
    main()