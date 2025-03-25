import sqlite3
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By  # ✅ FIXED MISSING IMPORT
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_NAME = os.getenv("BROWSING_DB", "browsing_history.db")

chrome_options = Options()
chrome_options.add_argument("--headless")  
service = Service()  

try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("chrome://history")

    # Extract browsing history
    browsing_data = []
    history_items = driver.find_elements(By.CLASS_NAME, "history-entry")
    for item in history_items:
        try:
            title = item.find_element(By.CLASS_NAME, "entry-title").text
            url = item.find_element(By.CLASS_NAME, "entry-link").get_attribute("href")
            browsing_data.append((title, url))
        except:
            continue

    driver.quit()

    print("✅ Browsing history extracted successfully!")

except Exception as e:
    print(f"❌ Error extracting browsing history: {e}")
