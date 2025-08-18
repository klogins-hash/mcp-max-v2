import asyncio
import json
import sys
import os
import aiohttp
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin, urlparse
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraperMCPServer:
    def __init__(self):
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=30)
        
    async def initialize(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        
    async def cleanup(self):
        if self.session:
            await self.session.close()
            
    async def handle_request(self, request):
        method = request.get('method')
        params = request.get('params', {})
        request_id = request.get('id')
        
        try:
            if method == 'tools/list':
                result = await self.list_tools()
            elif method == 'tools/call':
                result = await self.call_tool(params)
            else:
                return self.error_response(request_id, -32601, "Method not found")
                
            return {
                'jsonrpc': '2.0',
                'result': result,
                'id': request_id
            }
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.error_response(request_id, -32603, str(e))
            
    async def list_tools(self):
        return {
            'tools': [
                {
                    'name': 'scrape_webpage',
                    'description': 'Scrape and extract content from a webpage',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'url': {'type': 'string', 'description': 'URL to scrape'},
                            'selector': {'type': 'string', 'description': 'CSS selector to extract specific content (optional)'},
                            'extract_links': {'type': 'boolean', 'description': 'Extract all links from the page', 'default': False},
                            'extract_images': {'type': 'boolean', 'description': 'Extract all image URLs', 'default': False}
                        },
                        'required': ['url']
                    }
                },
                {
                    'name': 'extract_metadata',
                    'description': 'Extract metadata from a webpage (title, description, keywords)',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'url': {'type': 'string', 'description': 'URL to extract metadata from'}
                        },
                        'required': ['url']
                    }
                },
                {
                    'name': 'search_text',
                    'description': 'Search for specific text patterns in a webpage',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'url': {'type': 'string', 'description': 'URL to search'},
                            'pattern': {'type': 'string', 'description': 'Text or regex pattern to search for'},
                            'is_regex': {'type': 'boolean', 'description': 'Treat pattern as regex', 'default': False}
                        },
                        'required': ['url', 'pattern']
                    }
                }
            ]
        }
        
    async def call_tool(self, params):
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        
        if tool_name == 'scrape_webpage':
            return await self.scrape_webpage(arguments)
        elif tool_name == 'extract_metadata':
            return await self.extract_metadata(arguments)
        elif tool_name == 'search_text':
            return await self.search_text(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
            
    async def fetch_page(self, url):
        """Fetch webpage content"""
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.text(), response.url
            
    async def scrape_webpage(self, args):
        url = args['url']
        selector = args.get('selector')
        extract_links = args.get('extract_links', False)
        extract_images = args.get('extract_images', False)
        
        html, final_url = await self.fetch_page(url)
        soup = BeautifulSoup(html, 'html.parser')
        
        result = {
            'url': str(final_url),
            'title': soup.title.string if soup.title else None
        }
        
        # Extract specific content if selector provided
        if selector:
            elements = soup.select(selector)
            result['selected_content'] = [elem.get_text(strip=True) for elem in elements]
        else:
            # Get main text content
            for script in soup(["script", "style"]):
                script.decompose()
            result['text_content'] = soup.get_text(strip=True)[:5000]  # Limit to 5000 chars
        
        # Extract links if requested
        if extract_links:
            links = []
            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(str(final_url), link['href'])
                links.append({
                    'text': link.get_text(strip=True),
                    'url': absolute_url
                })
            result['links'] = links[:50]  # Limit to 50 links
        
        # Extract images if requested
        if extract_images:
            images = []
            for img in soup.find_all('img', src=True):
                absolute_url = urljoin(str(final_url), img['src'])
                images.append({
                    'alt': img.get('alt', ''),
                    'src': absolute_url
                })
            result['images'] = images[:50]  # Limit to 50 images
        
        return {
            'content': [{
                'type': 'text',
                'text': json.dumps(result, indent=2)
            }]
        }
        
    async def extract_metadata(self, args):
        url = args['url']
        html, final_url = await self.fetch_page(url)
        soup = BeautifulSoup(html, 'html.parser')
        
        metadata = {
            'url': str(final_url),
            'title': soup.title.string if soup.title else None,
            'meta_tags': {}
        }
        
        # Extract meta tags
        for meta in soup.find_all('meta'):
            if meta.get('name'):
                metadata['meta_tags'][meta['name']] = meta.get('content', '')
            elif meta.get('property'):
                metadata['meta_tags'][meta['property']] = meta.get('content', '')
        
        # Extract Open Graph data
        og_data = {}
        for meta in soup.find_all('meta', property=re.compile(r'^og:')):
            og_data[meta['property']] = meta.get('content', '')
        if og_data:
            metadata['open_graph'] = og_data
        
        # Extract Twitter Card data
        twitter_data = {}
        for meta in soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')}):
            twitter_data[meta['name']] = meta.get('content', '')
        if twitter_data:
            metadata['twitter_card'] = twitter_data
        
        return {
            'content': [{
                'type': 'text',
                'text': json.dumps(metadata, indent=2)
            }]
        }
        
    async def search_text(self, args):
        url = args['url']
        pattern = args['pattern']
        is_regex = args.get('is_regex', False)
        
        html, final_url = await self.fetch_page(url)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        
        matches = []
        if is_regex:
            regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            for match in regex.finditer(text):
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].strip()
                matches.append({
                    'match': match.group(),
                    'context': f"...{context}...",
                    'position': match.start()
                })
        else:
            # Simple text search
            pattern_lower = pattern.lower()
            text_lower = text.lower()
            index = 0
            while True:
                index = text_lower.find(pattern_lower, index)
                if index == -1:
                    break
                start = max(0, index - 50)
                end = min(len(text), index + len(pattern) + 50)
                context = text[start:end].strip()
                matches.append({
                    'match': text[index:index + len(pattern)],
                    'context': f"...{context}...",
                    'position': index
                })
                index += 1
        
        result = {
            'url': str(final_url),
            'pattern': pattern,
            'is_regex': is_regex,
            'match_count': len(matches),
            'matches': matches[:20]  # Limit to 20 matches
        }
        
        return {
            'content': [{
                'type': 'text',
                'text': json.dumps(result, indent=2)
            }]
        }
            
    def error_response(self, request_id, code, message):
        return {
            'jsonrpc': '2.0',
            'error': {'code': code, 'message': message},
            'id': request_id
        }

async def main():
    server = WebScraperMCPServer()
    await server.initialize()
    
    try:
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)
        
        while True:
            line = await reader.readline()
            if not line:
                break
            try:
                request = json.loads(line.decode().strip())
                response = await server.handle_request(request)
                print(json.dumps(response))
                sys.stdout.flush()
            except Exception as e:
                logger.error(f"Error: {e}")
    finally:
        await server.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
