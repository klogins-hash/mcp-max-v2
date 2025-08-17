#!/usr/bin/env python3
"""
Check existing Railway docs in Weaviate and scrape new ones
"""

import weaviate
import requests
from datetime import datetime
import json
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import hashlib

WEAVIATE_URL = "https://weaviate-production-5bc1.up.railway.app"
RAILWAY_DOCS_URL = "https://docs.railway.com/"

class RailwayDocsManager:
    def __init__(self):
        self.client = weaviate.Client(url=WEAVIATE_URL)
        self.existing_urls = set()
        self.existing_docs = {}
        
    def get_existing_docs(self):
        """Fetch all existing Railway docs from Weaviate"""
        print("Fetching existing Railway docs from Weaviate...")
        
        # Get all RailwayDocs with their URLs
        query = self.client.query.get("RailwayDocs", ["title", "url", "content", "scraped_at"]).with_limit(1000)
        result = query.do()
        
        docs = result.get('data', {}).get('Get', {}).get('RailwayDocs', [])
        print(f"Found {len(docs)} existing Railway docs in Weaviate")
        
        for doc in docs:
            url = doc.get('url', '')
            if url:
                self.existing_urls.add(url)
                self.existing_docs[url] = doc
                
        # Print sample of existing docs
        print("\nSample of existing docs:")
        for i, (url, doc) in enumerate(list(self.existing_docs.items())[:5]):
            print(f"  - {doc.get('title', 'No title')} ({url})")
            
        return self.existing_docs
    
    def scrape_railway_sitemap(self):
        """Scrape Railway docs sitemap to get all documentation URLs"""
        print("\nFetching Railway documentation sitemap...")
        
        all_urls = set()
        
        # Try sitemap first
        sitemap_url = urljoin(RAILWAY_DOCS_URL, "sitemap.xml")
        try:
            response = requests.get(sitemap_url, timeout=10)
            if response.status_code == 200:
                from xml.etree import ElementTree
                root = ElementTree.fromstring(response.content)
                
                # Extract URLs from sitemap
                for url in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
                    doc_url = url.text
                    if doc_url and "docs.railway.com" in doc_url:
                        all_urls.add(doc_url)
                        
                print(f"Found {len(all_urls)} URLs in sitemap")
        except:
            print("Could not fetch sitemap, will crawl main page")
            
        # Also crawl main documentation page
        try:
            response = requests.get(RAILWAY_DOCS_URL, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all documentation links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith('/'):
                        full_url = urljoin(RAILWAY_DOCS_URL, href)
                        all_urls.add(full_url)
                    elif href.startswith('https://docs.railway.com'):
                        all_urls.add(href)
                        
        except Exception as e:
            print(f"Error crawling main page: {e}")
            
        # Filter to only documentation URLs
        doc_urls = [url for url in all_urls if 'docs.railway.com' in url and not url.endswith('.xml')]
        print(f"Total documentation URLs found: {len(doc_urls)}")
        
        return doc_urls
    
    def scrape_doc_page(self, url):
        """Scrape a single documentation page"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = soup.find('h1')
            if not title:
                title = soup.find('title')
            title_text = title.text.strip() if title else "No title"
            
            # Extract main content
            content = ""
            
            # Try different content containers
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            
            if main_content:
                # Remove script and style elements
                for script in main_content(["script", "style"]):
                    script.decompose()
                    
                content = main_content.get_text(separator='\n', strip=True)
            else:
                # Fallback to body content
                body = soup.find('body')
                if body:
                    for script in body(["script", "style", "nav", "header", "footer"]):
                        script.decompose()
                    content = body.get_text(separator='\n', strip=True)
                    
            # Extract images
            images = []
            image_texts = []
            for img in soup.find_all('img'):
                src = img.get('src', '')
                alt = img.get('alt', '')
                if src:
                    images.append(src)
                if alt:
                    image_texts.append(alt)
                    
            return {
                'title': title_text,
                'content': content[:50000],  # Limit content size
                'url': url,
                'has_images': len(images) > 0,
                'image_count': len(images),
                'image_texts': ' '.join(image_texts),
                'scraped_at': datetime.utcnow().isoformat(),
                'content_hash': hashlib.md5(content.encode()).hexdigest()
            }
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def add_to_weaviate(self, doc_data):
        """Add a document to Weaviate"""
        try:
            # Create the object
            self.client.data_object.create(
                data_object=doc_data,
                class_name="RailwayDocs"
            )
            return True
        except Exception as e:
            print(f"Error adding to Weaviate: {e}")
            return False
    
    def update_railway_docs(self):
        """Main function to update Railway docs"""
        # Get existing docs
        self.get_existing_docs()
        
        # Get all current doc URLs
        current_urls = self.scrape_railway_sitemap()
        
        # Find new URLs
        new_urls = [url for url in current_urls if url not in self.existing_urls]
        print(f"\nFound {len(new_urls)} new documentation pages to scrape")
        
        if not new_urls:
            print("All Railway documentation is already up to date!")
            return
        
        # Scrape and add new docs
        added_count = 0
        failed_count = 0
        
        print("\nScraping new documentation pages...")
        for i, url in enumerate(new_urls):
            print(f"\r[{i+1}/{len(new_urls)}] Scraping: {url[:80]}...", end='', flush=True)
            
            doc_data = self.scrape_doc_page(url)
            if doc_data:
                if self.add_to_weaviate(doc_data):
                    added_count += 1
                else:
                    failed_count += 1
            else:
                failed_count += 1
                
            # Rate limiting
            time.sleep(0.5)
            
        print(f"\n\nScraping complete!")
        print(f"Successfully added: {added_count} documents")
        print(f"Failed: {failed_count} documents")
        print(f"Total Railway docs now: {len(self.existing_urls) + added_count}")

if __name__ == "__main__":
    manager = RailwayDocsManager()
    manager.update_railway_docs()
