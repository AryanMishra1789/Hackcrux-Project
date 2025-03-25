import sqlite3
import re
from collections import Counter
from textblob import TextBlob
import os
from dotenv import load_dotenv
load_dotenv()

DB_NAME = "emails.db"
YOUR_EMAIL = os.getenv("USER_EMAIL")

if not YOUR_EMAIL:
    raise ValueError("❌ USER_EMAIL is not set in .env file")
def fetch_sent_emails(limit=40):
    """Fetches last 40 emails sent by the user."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT body FROM emails 
    WHERE sender LIKE ? AND label NOT IN ('Trash', 'Spam') 
    ORDER BY timestamp DESC 
    LIMIT ?
""", (f"%{YOUR_EMAIL}%", limit))

    emails = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return emails if emails else []

def analyze_writing_style(emails):
    """Analyzes tone, sentence structure, common phrases, and formatting."""
    all_text = " ".join(emails)

    # 1️⃣ Determine Tone (Sentiment Analysis)
    sentiment = TextBlob(all_text).sentiment.polarity
    if sentiment > 0.3:
        tone = "Positive & Friendly"
    elif sentiment < -0.3:
        tone = "Serious & Formal"
    else:
        tone = "Neutral & Professional"

    # 2️⃣ Sentence Structure (Average Sentence Length)
    sentences = re.split(r'[.!?]', all_text)
    avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0

    # 3️⃣ Common Phrases (Most Frequent 3-Word Phrases)
    words = re.findall(r'\b\w+\b', all_text.lower())
    phrases = [" ".join(words[i:i+3]) for i in range(len(words) - 2)]
    common_phrases = Counter(phrases).most_common(5)

    # 4️⃣ Formatting & Special Characters
    has_emojis = bool(re.search(r'[^\w\s,]', all_text))  # Detect special characters like emojis
    has_bullets = "•" in all_text or "-" in all_text

    # Print Analysis
    print("\n✅ Writing Style Analysis (Sent Emails Only):")
    print(f"- **Tone:** {tone}")
    print(f"- **Average Sentence Length:** {avg_sentence_length:.1f} words")
    print(f"- **Common Phrases:** {[p[0] for p in common_phrases]}")
    print(f"- **Uses Emojis/Special Formatting?** {'Yes' if has_emojis else 'No'}")
    print(f"- **Uses Bullet Points?** {'Yes' if has_bullets else 'No'}")

    return {
        "tone": tone,
        "avg_sentence_length": avg_sentence_length,
        "common_phrases": [p[0] for p in common_phrases],
        "uses_emojis": has_emojis,
        "uses_bullets": has_bullets
    }

# Run the analysis
if __name__ == "__main__":
    past_emails = fetch_sent_emails()
    if past_emails:
        analyze_writing_style(past_emails)
    else:
        print("⚠️ No sent emails found. Make sure your email database is updated!")
