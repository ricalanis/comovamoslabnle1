import requests
from bs4 import BeautifulSoup
import re
from openai import OpenAI
import json

OPEN_AI_KEY = "{API KEY}"

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

def evaluate(evaluation_data, url_page):
    
    content = get_webpage_text(url_page)

    columns_data = str(evaluation_data['metadata']['columns'])

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful program with resources in open data standards and government data publishing practices. When evaluating datasets against standards, provide specific, accurate assessments and maintain strict only JSON and only JSON formatting always."
            ),
        },
        {
            "role": "user",
            "content": (
                content+ " " + columns_data + """
    Given this open data dataset, give me 3 data standards that could be used as a baseline to know which fields to publish an open data set with content that better matches the expectation of the data generated. Be specific of the standards given the theme or the area of the data published, not with generic data standards or open data guidelines, like gtfs for transit, or open contracting for data contracts . Grade this dataset with each of those data standards and provide a json for each of the standards, a structure that follows this one, only respond with a JSON like this:
    [
      {
        "standard": "[standard name]",
        "match_grade": "[grade, green, yellow, red],
        "dataset_link": "[standard url]"
      },
      {
        "standard": "[standard name]",
        "match_grade": "[grade, green, yellow, red]",
        "dataset_link": "[standard url]"
      },
      {
        "standard": "[standard name]",
        "match_grade": "[grade, green, yellow, red]",
        "dataset_link": "[standard url]"
      }
    ]
    ONLY AND ONLY RETRIEVE A JSON REPONSE, NOTHING ELSE. No descriptions. Only json"""
            ),
        },
    ]

    client = OpenAI(api_key=OPEN_AI_KEY, base_url="https://api.perplexity.ai")

    # chat completion without streaming
    response = client.chat.completions.create(
        model="llama-3.1-sonar-large-128k-online",
        messages=messages,
        temperature=0.5,
    )
    output = []
    try:
        output = json.loads(json.loads(response.json())['choices'][0]['message']['content'].replace("```",""))
        if isinstance(output, list):
            return output
    except:
        None
    return output