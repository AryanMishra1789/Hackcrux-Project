import faiss
import numpy as np
import sqlite3
from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Load FAISS index
index = faiss.read_index("browsing_history.index")

# Connect to database
conn = sqlite3.connect("browsing_history.db")
cursor = conn.cursor()

# Fetch browsing history
cursor.execute("SELECT id, title FROM history")
rows = cursor.fetchall()

# Store ID-to-Title mapping
id_to_title = {row[0]: row[1] for row in rows}

# Function to recommend similar searches
def recommend_similar_searches(query, top_n=5):
    """Finds and recommends similar search topics."""
    query_embedding = model.encode([query], normalize_embeddings=True)
    query_embedding = np.array(query_embedding).astype("float32")

    # Search FAISS index
    _, indices = index.search(query_embedding, top_n)

    # Retrieve recommended searches
    recommendations = [id_to_title.get(idx, "Unknown") for idx in indices[0]]

    return recommendations

# Example query
query = "Transformer Models"
recommended_searches = recommend_similar_searches(query)

print("\n🔍 **AI-Based Recommendations**")
for idx, rec in enumerate(recommended_searches, 1):
    print(f"{idx}. {rec}")
