import requests
from bs4 import BeautifulSoup

def scrape_problem_html(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Adjust selectors to target specific data (e.g., description, constraints)
    description = soup.find('div', {'class': 'problem-description'}).get_text(strip=True)
    constraints = soup.find('div', {'class': 'constraints'}).get_text(strip=True)
    return f"Description: {description}\nConstraints: {constraints}"

