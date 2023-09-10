#test to take img picture
import requests
from bs4 import BeautifulSoup

url = "https://www.nike.com/id/t/air-jordan-1-low-se-older-shoes-NDwhDt/DZ6333-083"
html = requests.get(url)
soup = BeautifulSoup(html.text, 'html.parser')

# Save the HTML content to a file
with open('response.html', 'w', encoding='utf-8') as file:
    file.write(html.text)

images = soup.find('span', class_='css-viwop1 u-full-width u-full-height css-147n82m css-yxqyqh')

print(images)
