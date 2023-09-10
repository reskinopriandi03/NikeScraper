#this code is scraping the img link, size, review only one product

import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By

# Set up the Chrome webdriver with the absolute path to ChromeDriver
chrome_driver_path = 'C:\\Users\\User\\Downloads\\chromedriver-win64\\chromedriver.exe'

# Initialize ChromeDriver
chrome_service = ChromeService(chrome_driver_path)
driver = webdriver.Chrome(service=chrome_service)

# URL of the webpage to scrape
url = 'https://www.nike.com/id/t/air-jordan-1-low-se-older-shoes-NDwhDt/DZ6333-083'

# Load the webpage
driver.get(url)

# Wait for the images to load (you may need to adjust the wait time)
driver.implicitly_wait(10)

# Find all image elements with class "d-sm-flx flx-jc-sm-fs flx-ai-sm-fe css-1mhv7vq"
image_elements = driver.find_elements(By.CSS_SELECTOR, '.d-sm-flx.flx-jc-sm-fs.flx-ai-sm-fe.css-1mhv7vq img')

# Extract the src attribute from each image element
image_urls = [img.get_attribute('src') for img in image_elements if img.get_attribute('src')]

# Find all elements with class "css-xf3ahq" (these are the size elements)
size_elements = driver.find_elements(By.CLASS_NAME, 'css-xf3ahq')

# Extract the size text from each size element
sizes = [size.text for size in size_elements]

# Combine image URLs into a single string separated by ||
image_urls_str = '||'.join(image_urls)

# Combine sizes into a single string separated by ||
sizes_str = '||'.join(sizes)


# Find the element containing the review and reviewers
review_element = driver.find_element(By.CLASS_NAME, 'css-ov1ktg')

# Extract the review text
review_text = review_element.find_element(By.CLASS_NAME, 'css-i2d2mu').text

# Extract the number of reviewers
reviewers_text = review_element.find_element(By.TAG_NAME, 'span').text

# Combine review and reviewers into a single string separated by ||
review_data_str = f'{review_text}||{reviewers_text}'

# Define the CSV file name
csv_file = 'link_image_size.csv'

# Write the combined data to the CSV file
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Image URLs', 'Sizes', 'review||reviewers'])  # Write the header row
    writer.writerow([image_urls_str, sizes_str, review_data_str])

# Close the webdriver
driver.quit()

print(f'Image URLs and Sizes saved to {csv_file}')
