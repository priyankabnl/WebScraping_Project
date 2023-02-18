import pandas as pd
import os
import requests
import selenium.webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options
options = Options()
options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
driver = selenium.webdriver.Firefox(options=options, executable_path='C:\webdrivers\geckodriver.exe')
path = os.path.join('C:' + os.sep, 'Users', 'Pbl', 'Automation _data', 'code''.csv')
data = pd.read_csv(path)

rows = []
AB = []
rowy = []

def chunker(seq, size):
   return (seq[i:i + size] for i in range(0, len(seq), size))

for j in chunker(data, 100):
    for ind in j.index:
        print(ind)
        url = "https://www.abc.com/s/search?q=" + str(data['cat_number'][ind]) + "&show=64"
        html_content = requests.get(url).text
        soup = BeautifulSoup(html_content, "lxml")
        k = soup.find_all("div", class_='row no-gutters')
        for div in k:
            all_items = div.find_all(class_='pr-4 col col-12')
            for item in all_items:
                title = item.text.strip()
                if title.find('Item #:'):
                    title = title.replace('CAT #:', "")
                    title = title.strip(' ')
                    if title == str(data['cat_number'][ind]):
                        rowy.append(title)
        for link in soup.find_all('a', href=True):
            if link['href'].startswith('/p/'):
                linky = "https://www.abc.com" + link['href']
                linkP = linky.split('/')
                for item in linkP:
                    if item == str(data['cat_number'][ind].lower()):
                        rows.append(linky)

for i in range(len(rows)):
    print(i)
    driver.get(rows[i])
    soup = BeautifulSoup(driver.page_source, "html.parser")
    i = soup.find_all('ul')
    for divy in i:
        AB.append(divy.text.strip().replace("\n", ""))
    pat = [w.replace('Categories', '') for w in AB]
    pat = [x.strip(' ') for x in pat]
    pat = [w.replace('              ', '>') for w in pat]

a = {'CAT': rowy, 'Category': pat}
df = pd.DataFrame.from_dict(a, orient='index')
df = df.transpose()
df.to_csv('output.csv',index= False)

driver.quit()
