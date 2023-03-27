import pandas as pd
import os
import requests
import selenium.webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait                 #### to protect from timeout
from selenium.webdriver.support import expected_conditions as EC
options = Options()
options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
driver = selenium.webdriver.Firefox(options=options, executable_path='C:\webdrivers\geckodriver.exe')
path = os.path.join('C:' + os.sep, 'Users', 'Pbl', 'Automation _data', 'code.csv')
data = pd.read_csv(path)

rows = []
AB = []
rowy = []

def chunker(seq, size):
   return (seq[i:i + size] for i in range(0, len(seq), size))

for j in chunker(data, 50):
    for ind in j.index:
        print(ind)
        url = "https://www.abc.com/s/search?q=" + str(data['cat_number'][ind])
        html_content = requests.get(url).text
        soup = BeautifulSoup(html_content, "lxml")
        k = soup.find_all("div", class_='row no-gutters')
        title_set = set()
        for div in k:
            all_items = div.find_all(class_='pr-4 col col-12')
            for item in all_items:
                title = item.text.strip()
                if title.find('Item #:'):
                    title = title.replace('CAT #:', "")
                    title = title.strip(' ')
                    if title == str(data['cat_number'][ind]):
                        if title not in title_set:  # Check if the link has already been added
                            title_set.add(title)
                            rowy.append(title)
                            print(title)
                            url2 = "https://www.abc.com/s/search?q=" + title
                            html_content2 = requests.get(url2).text
                            soup2 = BeautifulSoup(html_content2, "lxml")
                            count = 0
                            link_set = set()
                            for link in soup2.find_all("a", href=True):
                                if count == 1:
                                    break
                                if link['href'].startswith('/p/'):
                                    linky = "https://www.abc.com" + link['href']
                                    linkP = linky.split('/')
                                    for item in linkP:
                                        if item == str(data['cat_number'][ind].lower()):
                                            if linky not in link_set:  # Check if the link has already been added
                                                link_set.add(linky)  # Add the link to the set
                                                rows.append(linky)
                                                print(linky)
                                                count += 1


for i in range(len(rows)):
    print(i)
    driver.get(rows[i])
    try:
        element_present = EC.presence_of_element_located((By.XPATH, "//ul"))
        WebDriverWait(driver, 10).until(element_present)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        i = soup.find_all('ul')
        for divy in i:
            AB.append(divy.text.strip().replace("\n", ""))
        paty = [w.replace('Categories', '') for w in AB]
        paty = [x.strip(' ') for x in paty]
        paty = [w.replace('              ', '>') for w in paty]
    except:
        continue


a = {'CAT': rowy, 'Category': paty}
df = pd.DataFrame.from_dict(a, orient='index')
df = df.transpose()
df.to_csv('rally.csv',index= False)

driver.quit()
