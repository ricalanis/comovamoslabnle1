import requests
from bs4 import BeautifulSoup
import re
import openai
import json


def extract_webpage_text(url, timeout=30):
    """
    Fetches a webpage and extracts its text content, removing scripts, styles, and other non-content elements.
    
    Args:
        url (str): The URL of the webpage to fetch
        timeout (int): Request timeout in seconds
        
    Returns:
        str: Cleaned text content of the webpage
    
    Raises:
        requests.RequestException: If there's an error fetching the webpage
    """
    try:
        # Set a custom User-Agent to avoid potential blocks
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the webpage
        response = requests.get(url, headers=headers, timeout=timeout, verify=False)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'head', 'title', 'meta', '[document]']):
            element.decompose()
            
        # Get text and clean it
        text = soup.get_text()
        
        # Clean the extracted text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Remove extra whitespace and normalize spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
        
    except requests.RequestException as e:
        raise Exception(f"Error fetching webpage: {str(e)}")

def get_webpage_text(url):
    """
    Simplified wrapper function for quick text extraction.
    
    Args:
        url (str): The URL of the webpage
    
    Returns:
        str: Extracted text or error message
    """
    try:
        return extract_webpage_text(url)
    except Exception as e:
        return f"Error: {str(e)}"

    
def evaluate_dataset_page(page_content: str, api_key: str) -> dict:
    client = openai.OpenAI(api_key=api_key)
    
    prompt = """Evaluate the following dataset webpage content against these criteria, providing a score from 0-100 for each:

1. Does the data exist?
2. Is it available online from government in any form?
3. Is the dataset provided in machine-readable and reusable formats?
4. Is the machine-readable and reusable data available as a whole?
5. Is the dataset available free of charge?
6. Is the data openly licensed?
7. Is the dataset up to date?
8. Is the dataset being kept regularly updated?
9. Was it easy to find information about this dataset?
10. Are data identifiers provided for key elements in the dataset?

Provide your response in JSON format with criteria as keys and scores as values, plus a brief analysis. Include only these fields: scores (object with criteria and their scores), analysis (string with key findings). in a response that resembles 

{
  "scores": {
    "Does the data exist?": 100,
    "Is it available online from government in any form?": 100,
    "Is the dataset provided in machine-readable and reusable formats?": 100,
    "Is the machine-readable and reusable data available as a whole?": 100,
    "Is the dataset available free of charge?": 100,
    "Is the data openly licensed?": 100,
    "Is the dataset up to date?": 100,
    "Is the dataset being kept regularly updated?": 100,
    "Was it easy to find information about this dataset?": 85,
    "Are data identifiers provided for key elements in the dataset?": 90
  },
  "analysis": "The website is an official government site of the State of Nuevo Le\u00f3n which contains datasets including detailed information about public servants. The data is available in a reusable and machine-readable format (CSV). It looks like the data is kept updated regularly, with the last update timestamp visible. Data is provided free of charge and is openly licensed. Information about the dataset was somewhat easily found but could be presented in a clearer way. There was some evidence of data identifiers being used, though further examination would be needed to ascertain the comprehensiveness of these identifiers."
}



Webpage content:
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a data quality expert who evaluates open data portals. Provide numerical scores and brief analysis in a consistent json format."
            },
            {
                "role": "user",
                "content": prompt + page_content
            }
        ]
    )
    
    return json.loads(response.choices[0].message.content)
    
def evaluate(url):
    
    content = get_webpage_text(url)
    
    page_content = """**Skip to main content**...""" + content # Your provided content

    result = evaluate_dataset_page(page_content, "{API_KEY}")
    return result