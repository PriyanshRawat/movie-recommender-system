import pickle
import numpy as np
import pandas as pd
import re
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from thefuzz import process, fuzz

artifacts = {}
poster_lookup = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading model artifacts...")
    try:
        with open("artifacts/movies_df.pkl", "rb") as f:
            artifacts['movies_df'] = pickle.load(f)
        with open("artifacts/similarity.pkl", "rb") as f:
            artifacts['similarity'] = pickle.load(f)
        with open("artifacts/tmdb_to_ml.pkl", "rb") as f:
            artifacts['tmdb_to_ml'] = pickle.load(f)
        with open("artifacts/movie_id_search.pkl", "rb") as f:
            artifacts['movie_id_search'] = pickle.load(f)
            
        # Try loading trending, handle if missing
        try:
            with open("artifacts/trending.pkl", "rb") as f:
                artifacts['trending'] = pickle.load(f)
        except FileNotFoundError:
            print("Warning: trending.pkl not found. Cold start will be empty.")
            artifacts['trending'] = []

        loaded_sim = np.load("artifacts/movie_similarity.npy", allow_pickle=True)
        if loaded_sim.ndim == 0:
            artifacts['movie_similarity'] = loaded_sim.item()
        else:
            artifacts['movie_similarity'] = loaded_sim

    except Exception as e:
        print(f"Error loading artifacts: {e}")
        
    yield
    artifacts.clear()

app = FastAPI(lifespan=lifespan)

#Helper Functions

def cf_similarity(tmdb_id_1, tmdb_id_2):
    tmdb_to_ml = artifacts.get('tmdb_to_ml')
    movie_id_search = artifacts.get('movie_id_search')
    movie_similarity = artifacts.get('movie_similarity')

    if tmdb_id_1 not in tmdb_to_ml or tmdb_id_2 not in tmdb_to_ml: return 0.0
    ml_id_1, ml_id_2 = tmdb_to_ml[tmdb_id_1], tmdb_to_ml[tmdb_id_2]
    if ml_id_1 not in movie_id_search or ml_id_2 not in movie_id_search: return 0.0
    
    return movie_similarity[movie_id_search[ml_id_1], movie_id_search[ml_id_2]]

#API Endpoint
def _content_candidates(user_input, top_k=50):
    movies_df = artifacts['movies_df']
    similarity = artifacts['similarity']
    all_titles = movies_df['title'].tolist()
    
    # --- STRATEGY 1: SMART EXACT MATCH (Handles "spiderman", "ironman") ---
    def clean_text(text):
        return re.sub(r'[^a-zA-Z0-9]', '', str(text)).lower()

    cleaned_input = clean_text(user_input)
    cleaned_titles = movies_df['title'].apply(clean_text)
    exact_matches = movies_df[cleaned_titles == cleaned_input]
    
    if not exact_matches.empty:
        movie_index = exact_matches.index[0]
        
    else:
        # --- STRATEGY 2: ROBUST FUZZY MATCH (Handles "shawshank redeption") ---
        # We revert to 'token_sort_ratio' which is safer for typos in long phrases.
        # It prevents "RED" from matching "Redemption" just because it's a substring.
        best_match = process.extractOne(user_input, all_titles, scorer=fuzz.token_sort_ratio)
        
        # Threshold 65: Flexible enough for typos, strict enough to reject garbage
        if not best_match or best_match[1] < 65:
            return None, None 
            
        matched_title = best_match[0]
        matches = movies_df[movies_df['title'] == matched_title]
        if matches.empty:
            return None, None
            
        movie_index = matches.index[0]

    # Get Recommendations
    similar_movies = list(enumerate(similarity[movie_index]))
    sorted_similar_movies = sorted(similar_movies, key=lambda x: x[1], reverse=True)[1:top_k+1]
    
    return movie_index, sorted_similar_movies

@app.get("/recommend")
def recommend(title: str = "", alpha: float = 0.45, genre: str = "All"):
    movies_df = artifacts['movies_df']
    
    base_idx = None
    candidates = None

    # Only run search if title is not empty
    if title.strip():
        base_idx, candidates = _content_candidates(title, top_k=50)

    # --- COLD START BLOCK ---
    if base_idx is None:
        trending = artifacts.get('trending', [])
        
        if not trending:
            return {
                "source_movie": "Unknown", 
                "recommendations": [],
                "message": "Movie not found and no trending data available."
            }
            
        return {
            "source_movie": "Trending Movies (Cold Start)",
            "recommendations": [
                {
                    "title": m['title'], 
                    "score": float(m.get('vote_average', 0))/10, 
                    "tmdb_id": int(m['tmdbId']),  # <--- FIXED: Changed 'tmdb_id' to 'tmdbId'
                    "poster_url": poster_lookup.get(m['tmdbId'], f"https://placehold.co/400x600/2c3e50/ffffff?text={m['title'].replace(' ', '+')}") # <--- FIXED HERE TOO
                } for m in trending[:10]
            ]
        }

    # --- NORMAL RECOMMENDATION BLOCK ---
    base_movie = movies_df.iloc[base_idx]
    rescored = []

    for idx, content_score in candidates:
        candidate = movies_df.iloc[idx]
        
        # Genre Filter
        if genre != "All":
            cand_genres = candidate.genres if isinstance(candidate.genres, list) else []
            if genre not in cand_genres:
                continue

        # Hybrid Score
        cf_score = cf_similarity(base_movie.tmdbId, candidate.tmdbId)
        final_score = alpha * content_score + (1 - alpha) * cf_score
        
        poster_url = poster_lookup.get(candidate.tmdbId)
        if not poster_url:
            safe_title = candidate.title.replace(" ", "+")
            poster_url = f"https://placehold.co/400x600/2c3e50/ffffff?text={safe_title}"

        rescored.append({
            "title": candidate.title,
            "score": float(final_score),
            "tmdb_id": int(candidate.tmdbId),
            "poster_url": poster_url
        })

    rescored.sort(key=lambda x: x["score"], reverse=True)
    
    # Handle empty result after filtering
    if not rescored:
         return {
            "source_movie": base_movie.title,
            "recommendations": [],
            "message": f"No '{genre}' movies found similar to this."
         }

    return {
        "source_movie": base_movie.title,
        "recommendations": rescored[:10]
    }