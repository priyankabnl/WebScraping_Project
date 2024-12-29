import pandas as pd
import os
import time
import subprocess
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import TimeoutException
import requests

# Configure WebDriver options and service
options = Options()
options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
options.add_argument("--headless")  # Run in headless mode
service = Service(r'C:\webdrivers\geckodriver.exe')

driver = None  # Initialize driver as None

def restart_driver():
    """Restart the WebDriver to free memory and avoid crashes."""
    global driver
    try:
        if driver is not None:
            driver.quit()
            print("WebDriver quit successfully.")
    except Exception as e:
        print(f"Error while quitting WebDriver: {e}")
    finally:
        try:
            driver = webdriver.Firefox(service=service, options=options)
            print("WebDriver restarted successfully.")
        except Exception as e:
            print(f"Error while restarting WebDriver: {e}")
            driver = None

# Initialize WebDriver
restart_driver()

input_csv_file = r"C:\Users\PBansal\Desktop\Automation _data\code_cat.csv"
data = pd.read_csv(input_csv_file, dtype=str)

rows, AB, rowy = [], [], []

# Chunker function to split data
def chunker(seq, size):
    return (seq[i:i + size] for i in range(0, len(seq), size))

# Fetch product links
for j in chunker(data, 50):
    for ind in j.index:
        cat_number = str(data['cat_number'][ind]).strip()
        print(f"Processing CAT number: {cat_number}")
        url = f'https://www.usa.com/s/search?q={cat_number}'
        try:
            html_content = requests.get(url, timeout=10).text
            soup = BeautifulSoup(html_content, 'lxml')

            product_found = False
            for div in soup.find_all('div', class_='row no-gutters'):
                all_items = div.find_all(class_='pr-4 col col-12')
                for item in all_items:
                    title = item.text.strip().replace('CAT #:', "").strip()
                    if title == cat_number:
                        for link in soup.find_all('a', href=True):
                            if link['href'].startswith('/p/') and cat_number.lower() in link['href']:
                                linky = 'https://www.usa.com' + link['href']
                                rows.append(linky)
                                print(f"Hyperlink matched: {linky}")
                                product_found = True
                                break
                        if not product_found:
                            rows.append("No Link Found")
                        rowy.append(cat_number)
                        break
                if product_found or not product_found:
                    break
        except Exception as e:
            print(f"Error fetching product link for CAT {cat_number}: {e}")
            rows.append("No Link Found")
            rowy.append(cat_number)

# Scrape categories using Selenium
for index, link in enumerate(rows):
    print(f"Scraping details for link index {index}: {link}")
    if link == "No Link Found":
        AB.append("No Category Found")
        continue

    try:
        # Restart WebDriver every 50 links
        if index > 0 and index % 50 == 0:
            print("Restarting WebDriver to free memory...")
            restart_driver()
            if driver is None:
                print("WebDriver unavailable. Skipping...")
                AB.append("No Category Found")
                continue

        driver.get(link)
        time.sleep(2)  # Throttle requests
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//ul")))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        ul_elements = soup.find_all('ul')
        categories = '>'.join([ul.text.strip() for ul in ul_elements]).replace('Categories', '').replace("\n", "")
        AB.append(categories)
    except TimeoutException:
        print(f"Timeout for link at index {index}.")
        AB.append("Timeout")
    except Exception as e:
        print(f"Error scraping link {index}: {e}")
        AB.append("No Category Found")

# Clean up and save results
if driver is not None:
    driver.quit()

df = pd.DataFrame({'CAT': rowy, 'Links': rows, 'RexelCategory': AB})
df.to_excel(f"{os.path.splitext(input_csv_file)[0]}_Cat.xlsx", index=False)
print("File has been created.")
