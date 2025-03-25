import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse
from keybert import KeyBERT

# Database setup
DB_NAME = "browsing_history.db"

# List of URLs to exclude
EXCLUDE_DOMAINS = ["google.com/search", "mail.google.com", "facebook.com", "twitter.com"]

# Initialize KeyBERT Model
kw_model = KeyBERT()

# Categorization rules
CATEGORIES = {
    "AI": ["machine learning", "deep learning", "GPT", "transformer", "LLM"],
    "Web Dev": ["JavaScript", "React", "Next.js", "Tailwind", "CSS"],
    "Finance": ["stocks", "crypto", "trading", "investment"],
    "Quantum Computing": ["quantum", "Qiskit", "superposition"]
}

# Initialize Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
service = Service("/opt/homebrew/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

def create_table():
    """Creates a table for storing browsing history with category support."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE,
        title TEXT,
        timestamp TEXT
    )
    ''')
    
    # Add category column (ignore if exists)
    try:
        cursor.execute("ALTER TABLE history ADD COLUMN category TEXT;")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()
    conn.close()

def categorize_title(title):
    """Categorizes a browsing history title using predefined rules."""
    keywords = kw_model.extract_keywords(title, keyphrase_ngram_range=(1, 2), stop_words="english", top_n=3)
    detected_category = "Other"
    
    for category, terms in CATEGORIES.items():
        if any(term.lower() in title.lower() for term in terms):
            detected_category = category
            break
    
    return detected_category

def store_browsing_data(url, title, timestamp):
    """Stores browsing history in the SQLite database with categorization."""
    parsed_url = urlparse(url)
    domain = f"{parsed_url.netloc}{parsed_url.path}"
    
    if any(exclude in domain for exclude in EXCLUDE_DOMAINS):
        return  # Skip unwanted domains
    
    category = categorize_title(title)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO history (url, title, timestamp, category) VALUES (?, ?, ?, ?)",
                   (url, title, timestamp, category))
    conn.commit()
    conn.close()

def extract_browsing_history():
    """Extract browsing history and store in the database."""
    try:
        history_data = [
            ("https://arxiv.org/abs/2403.12345", "Latest Paper on Transformers", time.strftime('%Y-%m-%d %H:%M:%S')),
            ("https://huggingface.co/blog/llm-performance", "Hugging Face LLM Performance Guide", time.strftime('%Y-%m-%d %H:%M:%S')),
            ("https://google.com/search?q=best+python+frameworks", "Google Search", time.strftime('%Y-%m-%d %H:%M:%S'))
        ]  # Mock data for testing
        
        for url, title, timestamp in history_data:
            store_browsing_data(url, title, timestamp)
        
        print("✅ Browsing history extracted, categorized, and stored successfully!")
    except Exception as e:
        print(f"❌ Error extracting browsing history: {e}")
    
if __name__ == "__main__":
    create_table()
    extract_browsing_history()
