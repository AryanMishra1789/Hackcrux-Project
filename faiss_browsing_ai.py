# import sqlite3
# import faiss
# import numpy as np
# from sentence_transformers import SentenceTransformer

# # Load Sentence Transformer model
# model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# # Connect to SQLite database
# conn = sqlite3.connect("browsing_history.db")
# cursor = conn.cursor()

# # Fetch browsing history
# cursor.execute("SELECT id, title FROM history WHERE title IS NOT NULL AND title != ''")
# data = cursor.fetchall()

# if not data:
#     print("⚠️ No valid browsing history found!")
#     exit()

# # Extract IDs and Titles
# ids, titles = zip(*data)
# id_array = np.array(ids, dtype=np.int64)  # Convert to FAISS-compatible ID format

# # Compute embeddings
# embeddings = model.encode(titles, normalize_embeddings=True)
# embeddings = np.array(embeddings).astype("float32")

# # Create FAISS index with ID mapping
# d = embeddings.shape[1]
# index = faiss.IndexFlatIP(d)  # Inner Product similarity
# index = faiss.IndexIDMap(index)  # Map FAISS vectors to database IDs
# index.add_with_ids(embeddings, id_array)  # Store explicit IDs

# # Save FAISS index
# faiss.write_index(index, "browsing_history.index")
# print("✅ FAISS index created and saved successfully!")

# # Close database connection
# conn.close()


import faiss
import numpy as np
import sqlite3
from sentence_transformers import SentenceTransformer

# Load Sentence Transformer model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Function to recommend similar searches
def recommend_similar_searches(query, top_n=5, similarity_threshold=0.2):
    """Finds and recommends diverse search topics with expanded search range."""
    
    # Open database connection
    conn = sqlite3.connect("browsing_history.db")
    cursor = conn.cursor()

    # Load FAISS index
    index = faiss.read_index("browsing_history.index")

    # Fetch browsing history (ID-Title mapping)
    cursor.execute("SELECT id, title FROM history")
    rows = cursor.fetchall()
    id_to_title = {row[0]: row[1] for row in rows}

    # Compute query embedding
    query_embedding = model.encode([query], normalize_embeddings=True)
    query_embedding = np.array(query_embedding).astype("float32")

    # Search FAISS index (expand search pool to 10)
    scores, indices = index.search(query_embedding, top_n * 3)

    # Convert FAISS results from indices to actual SQLite IDs
    unique_recommendations = []
    seen_titles = set()

    for idx, score in zip(indices[0], scores[0]):
        title = id_to_title.get(int(idx), "Unknown")

        # Only add if the similarity score is above threshold and it's not a duplicate
        if title not in seen_titles and title != "Unknown" and score >= similarity_threshold:
            seen_titles.add(title)
            unique_recommendations.append(title)

        if len(unique_recommendations) >= top_n:
            break  # Stop once we have enough unique recommendations

    # If we have fewer than `top_n` recommendations, fill with diverse topics (keeping connection open)
    if len(unique_recommendations) < top_n:
        remaining_slots = top_n - len(unique_recommendations)
        cursor.execute("SELECT DISTINCT title FROM history ORDER BY RANDOM() LIMIT ?", (remaining_slots,))
        backup_recommendations = [row[0] for row in cursor.fetchall()]
        unique_recommendations.extend(backup_recommendations)

    # Close database connection
    conn.close()

    return unique_recommendations

# Example query test
query = "Transformer Models"
recommended_searches = recommend_similar_searches(query)

print("\n🔍 **AI-Based Recommendations (Diverse Titles)**")
for idx, rec in enumerate(recommended_searches, 1):
    print(f"{idx}. {rec}")
