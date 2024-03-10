import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Setup for Firefox and Selenium WebDriver
options = Options()
options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
driver = webdriver.Firefox(options=options, executable_path='C:\webdrivers\geckodriver.exe')

# CSV file path
input_csv_file = r"C:\Users\PBansal\Desktop\Automation _data\code.csv"
data = pd.read_csv(input_csv_file, dtype=str)

# Lists to store scraped data
rows = []  # To store the hyperlinks
AB = []  # To store the categories
rowy = []  # To store the CAT numbers

def chunker(seq, size):
   return (seq[i:i + size] for i in range(0, len(seq), size))

for j in chunker(data, 50):
    for ind in j.index:
        cat_number = str(data['cat_number'][ind]).strip()
        print(f"Processing CAT number: {cat_number}")

        url = f'https://www.website.com/s/search?q={cat_number}'
        html_content = requests.get(url).text
        soup = BeautifulSoup(html_content, 'lxml')

        product_found = False

        # Search for product containers
        for div in soup.find_all('div', class_='row no-gutters'):
            all_items = div.find_all(class_='pr-4 col col-12')

            for item in all_items:
                title = item.text.strip().replace('CAT #:', "").strip()
                print(f"Extracted Title: '{title}'")

                if title == cat_number:
                    # Search for the hyperlink
                    for link in soup.find_all('a', href=True):
                        if link['href'].startswith('/p/') and cat_number.lower() in link['href']:
                            linky = 'https://www.usa.com' + link['href']
                            rows.append(linky)  # Add the hyperlink to the rows list
                            print(f"Hyperlink matched: {linky}")
                            product_found = True
                            break

                    if not product_found:
                        rows.append("No Link Found")
                    rowy.append(cat_number)  # Add the CAT number to the rowy list
                    break  # Break from all_items loop once processed

            if product_found or not product_found:
                break  # Break from div loop once processed



# Selenium WebDriver to navigate to each hyperlink and scrape additional details
for index, link in enumerate(rows):
    print(f"Scraping details for link index {index}: {link}")
    if link == "No Link Found":
        AB.append("No Category Found")
        continue

    try:
        driver.get(link)
        # Wait for the required elements to load on the page
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//ul")))

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        ul_elements = soup.find_all('ul')
        # Assuming the first <ul> has the category information
        categories = '>'.join([ul.text.strip() for ul in ul_elements]).replace('Categories', '').replace("\n", "")
        AB.append(categories)
    except TimeoutException:
        print(f"Page load timed out for link at index {index}.")
        AB.append("Page Load Timeout")  # Append a specific placeholder for this error
    except Exception as e:
        print(f"An exception occurred while scraping link at index {index}: {e}")
        AB.append("No Category Found")

driver.quit()

# Create DataFrame and save to CSV
df = pd.DataFrame({
    'CAT': rowy,
    'Links': rows,
    'RexelCategory': AB
})
df['CAT'] = "" + df['CAT'].astype(str)

# Define your output file path
output_file = f"{os.path.splitext(input_csv_file)[0]}_relCat.xlsx"

df.to_excel(output_file, index=False)

print("File has been created.")
