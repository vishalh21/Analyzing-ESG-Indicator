
# Packages to be installed: selenium, beautifulsoup4, webdriver-manager

import os
import time
import json
import pandas as pd
import requests  # Used for static sites
from selenium import webdriver  # Used for dynamic sites
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager  
from bs4 import BeautifulSoup

# Input things

# Extracting data of NIFTY500 Stocks from the file
FILE_PATH = 'ind_nifty500list.xlsx'
df = pd.DataFrame(pd.read_excel(FILE_PATH))
stocks = [x for x in df.Symbol]
stock_names = [x for x in df['Company Name']]
stocks = stocks[1 : 21]
stock_names = stock_names[1 : 21]

# Creating 2 dynamic webdriver one for crawling through website and one for downloading pdfs
driver = webdriver.Chrome(ChromeDriverManager().install()) 
pdf_dn = webdriver.Chrome(ChromeDriverManager().install()) 

url = "https://trendlyne.com/"
driver.get(url)
WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Search Stocks"]')))  # Waiting for the site to load... Dynamic webpage :(

#####
for i, stock_name in enumerate(stock_names):
    # Maintaining a log to keep track of things
    stock = stocks[i]
    log_file = open('download_log.txt', 'a+')
    log_file.write(f'{stock} - ')
    try: 
        driver.get(url)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Search Stocks"]')))
        srchbox = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Search Stocks"]')  # Loaction to search box of site
        srchbox.clear()
        srchbox.send_keys(stock_name)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'div[id="{stock}"]')))
        soup = BeautifulSoup(driver.page_source, "html.parser")
    except:
        try:
            srchbox = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Search Stocks"]')  # Loaction to search box of site
            srchbox.clear()
            srchbox.send_keys(stock)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'div[id="{stock}"]')))
            soup = BeautifulSoup(driver.page_source, "html.parser")
        except:
            log_file.write('Failed\n')
            log_file.close()
            continue

    tmp_link = driver.find_element(By.CSS_SELECTOR, f'div[id="{stock}"]').find_element(by=By.TAG_NAME, value="a").get_attribute("href")
    full_link = url + "fundamentals/annual-results/" + tmp_link.split('equity/')[1]

    try:
        driver.get(full_link)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[class="colorTLblue"]')))
        soup = BeautifulSoup(driver.page_source, "html.parser")
    except:
        log_file.write('No Past Records :(\n')
        log_file.close()
        continue

    doc_list = [link['href'] for link in soup.select('a.colorTLblue') if len(link['href'].split('/get-document/')) != 1]

    try: os.mkdir(stock)
    except: pass
    os.chdir(stock)
    progress = 0
    for doc_link in doc_list:
        pdf_dn.get(doc_link)
        try:
            WebDriverWait(pdf_dn, 5).until(EC.url_matches(".amazonaws.com/*"))
        except:
            pass
        doc_name = pdf_dn.current_url.split('.pdf')[0].split('/')[-1] + '.pdf'
        responsee = requests.get(pdf_dn.current_url)
        open(doc_name, 'wb').write(responsee.content)
        progress += 1
    os.chdir('../')
    log_file.write(f'{progress} Done\n')
    log_file.close()