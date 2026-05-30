"""Extraction service for downloading and cleaning web page content."""

import httpx
from bs4 import BeautifulSoup


async def extract_content(url: str) -> str:
    """
    Download a web page and extract its main text content.

    Args:
        url: The URL of the web page to extract.

    Returns:
        The cleaned text content of the page, or an empty string if it fails.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
                element.decompose()
    
            text = soup.get_text(separator=" ")
            
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            cleaned_text = "\n".join(chunk for chunk in chunks if chunk)
            
            return cleaned_text
            
    except Exception as e:
        print(f"Failed to extract content from {url}: {e}")
        return ""
