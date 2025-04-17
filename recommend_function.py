import pandas as pd
import ast

# === Load Dataset and Precomputed Similarity Matrix ===
df_full = pd.read_csv("v8_ready_to_combine_vector.csv")
sim_matrix_df = pd.read_csv("precomputed_similar_movies_chunked.csv")

# Convert stringified lists back to real lists
sim_matrix_df["top_similar_movies"] = sim_matrix_df["top_similar_movies"].apply(ast.literal_eval)
sim_matrix_df["similarity_scores"] = sim_matrix_df["similarity_scores"].apply(ast.literal_eval)

# Normalize titles for consistency
sim_matrix_df['movie'] = sim_matrix_df['movie'].str.strip().str.lower()
df_full['title'] = df_full['title'].str.strip().str.lower()


def get_similar_movies(title: str, top_n: int = 5):
    """
    Retrieve top-N similar movies based on a precomputed similarity matrix.
    Returns a list of dicts with title, similarity score, and genre.
    """
    try:
        title = title.strip().lower()
        print(f"🔍 Looking for title: {title}")

        matches = sim_matrix_df[sim_matrix_df['movie'] == title]
        print(f"🧾 Matches found: {len(matches)}")

        if matches.empty:
            return []

        row = matches.iloc[0]
        titles = row['top_similar_movies']
        scores = row['similarity_scores']

        results = []
        for m, s in zip(titles[:top_n], scores[:top_n]):
            m_clean = m.strip().lower()
            genre = df_full[df_full['title'] == m_clean].iloc[0].get("genre", "Unknown")
            results.append({"title": m, "similarity": s, "genre": genre})

        return results

    except Exception as e:
        print(f"❌ Error in get_similar_movies: {e}")
        return []
