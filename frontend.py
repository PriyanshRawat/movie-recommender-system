import streamlit as st
import requests
import time
import urllib.parse
import os
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
# Load environment variables (Create a .env file with OMDB_API_KEY=your_key)
load_dotenv()

API_URL = "http://127.0.0.1:8000/recommend"

# 👇 PASTE YOUR OMDb KEY HERE (Or use .env file)
OMDB_API_KEY = os.getenv("OMDB_API_KEY", "a0deaf55")

st.set_page_config(
    page_title="MovieMatch AI",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="collapsed" # Hides sidebar by default
)

# -----------------------------------------------------------------------------
# CUSTOM CSS (Modern Dark Theme)
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    /* Hide Sidebar completely */
    [data-testid="stSidebar"] {display: none;}
    
    /* Main Title Styling */
    .big-font {
        font-size: 50px !important;
        font-weight: 800;
        color: #E50914; /* Netflix Red */
        text-align: center;
        margin-bottom: 5px;
    }
    .subtitle {
        font-size: 18px !important;
        font-weight: 300;
        text-align: center;
        margin-bottom: 30px;
        color: #b3b3b3;
    }
    
    /* Card Styling */
    div[data-testid="stContainer"] {
        background-color: #262730;
        border-radius: 12px;
        padding: 15px;
        transition: transform 0.2s;
        border: 1px solid #333;
    }
    div[data-testid="stContainer"]:hover {
        transform: translateY(-5px);
        border-color: #E50914;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------
# 1. Add this decorator above the function
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_poster_omdb(movie_title):
    if OMDB_API_KEY and OMDB_API_KEY != "PASTE_YOUR_KEY_HERE":
        try:
            url = f"http://www.omdbapi.com/?t={movie_title}&apikey={OMDB_API_KEY}"
            response = requests.get(url)
            data = response.json()
            if data.get('Response') == 'True' and data.get('Poster') != 'N/A':
                return data.get('Poster')
        except Exception:
            pass 

    safe_title = urllib.parse.quote(movie_title)
    return f"https://placehold.co/400x600/2c3e50/ffffff?text={safe_title}&font=roboto"

def get_recommendations(title, genre, alpha=0.45):
    try:
        # If title is empty, we send empty string, backend handles trending
        params = {"title": title, "alpha": alpha, "genre": genre}
        response = requests.get(API_URL, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# def score_to_stars(score):
#     stars = int(score * 5)
#     return "⭐" * stars if stars > 0 else "⭐"

# -----------------------------------------------------------------------------
# MAIN APP LAYOUT
# -----------------------------------------------------------------------------

# 1. Header
st.markdown('<p class="big-font">MovieMatch AI</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Discover your next favorite movie.</p>', unsafe_allow_html=True)

# 2. Search & Filter Bar (All in one row)
# Columns: [Search Box (3) | Genre Filter (1) | Search Button (1)]
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    search_query = st.text_input("Search Movie", placeholder="Enter movie name (e.g. Inception)...", label_visibility="collapsed")

with col2:
    # Genre list matching your backend logic
    genre_options = ["All", "Action", "Comedy", "Drama", "Thriller", "Sci-Fi", "Romance", "Adventure", "Horror", "Animation"]
    selected_genre = st.selectbox("Genre", genre_options, label_visibility="collapsed")

with col3:
    # use_container_width makes the button fill the column
    search_btn = st.button("🚀 Find Movies", type="primary", use_container_width=True)

# 3. Logic & Display
# Trigger if button clicked OR if query is empty (shows trending on load)
if search_btn or search_query == "":
    
    st.divider()
    
    with st.spinner("🤖 Curating your list..."):
        # Add slight delay for UX feel
        if search_query: time.sleep(0.3)
        data = get_recommendations(search_query, selected_genre)

    if data:
        source_movie = data['source_movie']
        recommendations = data['recommendations']
        message = data.get('message', "") # Get backend message if exists

        # --- SMART MESSAGING LOGIC ---
        
        # Scenario 1: Backend returned Trending (Cold Start)
        if "Trending" in source_movie or "Unknown" in source_movie:
            if search_query.strip() == "":
                # User didn't type anything
                st.subheader("🔥 Top Trending Movies")
                st.caption("Here is what's popular right now:")
            else:
                # User typed something but it wasn't found
                st.warning(f"⚠️ We couldn't find **'{search_query}'**. Showing trending movies instead.")
        
        # Scenario 2: Successful Recommendation
        else:
            st.subheader(f"🎬 Because you watched *{source_movie}*")
            if selected_genre != "All":
                st.caption(f"Showing **{selected_genre}** movies similar to it:")
        
        # --- GRID DISPLAY ---
        if not recommendations and message:
             st.info(message)
        else:
            cols = st.columns(5)
            for i, movie in enumerate(recommendations):
                with cols[i % 5]:
                    with st.container():
                        # Poster
                        poster_url = fetch_poster_omdb(movie['title'])
                        st.image(poster_url, use_container_width=True)
                        
                        # Title
                        title = movie['title']
                        if len(title) > 22: title = title[:20] + "..."
                        st.markdown(f"**{title}**")
                        
                        # Rating
                        #stars = score_to_stars(movie['score'])
                        st.caption(f"{movie['score']:.2f}")
                        
                        # Popover
                        with st.popover("Details"):
                            st.markdown(f"**{movie['title']}**")
                            st.info(f"Match Score: {movie['score']:.4f}")
                            st.text(f"TMDB ID: {movie['tmdb_id']}")

    elif search_query:
        # If API fails completely (Server Error)
        st.error("❌ Error connecting to server. Is the backend running?")