"""
MovieMatch AI — Frontend v2 (cinematic redesign).

Pure view layer over the existing FastAPI backend; frontend.py is untouched.
Run (separate terminal from the backend, repo root):

    python -m streamlit run frontend_v2.py --server.port 8502

Backend must be running:  python -m uvicorn main:app --reload
"""

import html
import os
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/recommend")
OMDB_API_KEY = os.getenv("OMDB_API_KEY", "")

GENRES = ["All", "Action", "Adventure", "Animation", "Comedy", "Drama",
          "Horror", "Romance", "Science Fiction", "Thriller"]

st.set_page_config(
    page_title="MovieMatch AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------- styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@400;500;600&display=swap');

/* App shell */
[data-testid="stSidebar"], [data-testid="stToolbar"], footer, #MainMenu {display:none;}
.stApp {
    background:
        radial-gradient(1100px 500px at 15% -10%, rgba(229,9,20,.16), transparent 60%),
        radial-gradient(900px 450px at 85% -10%, rgba(88,86,214,.18), transparent 60%),
        #0b0d13;
    font-family: 'Inter', sans-serif;
}
.block-container {padding-top: 2.2rem; max-width: 1200px;}

/* Hero */
.hero-title {
    font-family:'Outfit',sans-serif; font-weight:800; font-size:56px; line-height:1.05;
    text-align:center; margin:0;
    background: linear-gradient(92deg, #ffffff 15%, #ff5f6d 55%, #e50914 85%);
    -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
}
.hero-sub {text-align:center; color:#9aa1b1; font-size:17px; font-weight:300; margin:10px 0 26px;}
.hero-sub b {color:#cfd4e0; font-weight:600;}

/* Inputs */
div[data-baseweb="input"], div[data-baseweb="select"] > div {
    background:#141824 !important; border:1px solid #262c3d !important; border-radius:12px !important;
}
div[data-baseweb="input"]:focus-within {border-color:#e50914 !important; box-shadow:0 0 0 3px rgba(229,9,20,.18);}
.stTextInput input {color:#eceff5 !important; font-size:15px;}
.stButton > button {
    background:linear-gradient(135deg,#e50914,#b00710) !important; color:#fff !important;
    border:none !important; border-radius:12px !important; font-weight:600 !important;
    height:2.6rem; transition:filter .15s ease, transform .15s ease;
}
.stButton > button:hover {filter:brightness(1.15); transform:translateY(-1px);}

/* Section heading */
.section-head {display:flex; align-items:baseline; gap:12px; margin:6px 0 4px;}
.section-head h2 {font-family:'Outfit',sans-serif; font-weight:600; font-size:26px; color:#f2f4f9; margin:0;}
.section-head span {color:#8b93a7; font-size:14px;}

/* Card grid */
.mm-grid {display:grid; grid-template-columns:repeat(auto-fill,minmax(180px,1fr)); gap:20px; margin-top:14px;}
.mm-card {
    position:relative; border-radius:16px; overflow:hidden; background:#12151f;
    border:1px solid #232838; transition:transform .22s ease, border-color .22s ease, box-shadow .22s ease;
}
.mm-card:hover {transform:translateY(-6px); border-color:rgba(229,9,20,.65); box-shadow:0 14px 34px rgba(0,0,0,.55);}
.mm-poster {position:relative; aspect-ratio:2/3; overflow:hidden;}
.mm-poster img {width:100%; height:100%; object-fit:cover; display:block; transition:transform .35s ease;}
.mm-card:hover .mm-poster img {transform:scale(1.06);}
.mm-poster::after {
    content:''; position:absolute; inset:0;
    background:linear-gradient(180deg, transparent 55%, rgba(11,13,19,.92) 100%);
}
.mm-rank {
    position:absolute; top:10px; left:10px; z-index:2;
    background:rgba(11,13,19,.78); backdrop-filter:blur(4px); border:1px solid #2c3348;
    color:#dfe3ee; font-size:12px; font-weight:600; padding:3px 9px; border-radius:999px;
}
.mm-imdb {
    position:absolute; top:10px; right:10px; z-index:2;
    background:rgba(245,197,24,.95); color:#1a1400; font-weight:700; font-size:12px;
    padding:3px 8px; border-radius:8px;
}
.mm-body {padding:12px 14px 14px;}
.mm-title {
    color:#f4f6fb; font-weight:600; font-size:14.5px; line-height:1.3;
    display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;
    min-height:2.6em; margin-bottom:9px;
}
.mm-genres {display:flex; flex-wrap:wrap; gap:6px; min-height:22px;}
.mm-genre {
    background:#1b2030; border:1px solid #2c3348; color:#aab2c5;
    font-size:11px; font-weight:500; padding:2px 9px; border-radius:999px; white-space:nowrap;
}

/* Banners */
.mm-note {
    background:#141824; border:1px solid #262c3d; border-left:4px solid #e50914;
    color:#c9cfdd; border-radius:10px; padding:12px 16px; font-size:14px; margin-top:10px;
}
.mm-footer {text-align:center; color:#565e72; font-size:12.5px; margin-top:44px;}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------- data
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_omdb_data(title: str):
    """Poster URL, IMDb rating and genres for a title. Graceful fallback without a key."""
    safe = urllib.parse.quote(title)
    poster = f"https://placehold.co/400x600/141824/8b93a7?text={safe}&font=roboto"
    rating = "N/A"
    genres = []
    if OMDB_API_KEY:
        try:
            r = requests.get("https://www.omdbapi.com/",
                             params={"t": title, "apikey": OMDB_API_KEY}, timeout=5)
            d = r.json()
            if d.get("Response") == "True":
                if d.get("Poster") and d.get("Poster") != "N/A":
                    poster = d["Poster"]
                if d.get("imdbRating") and d.get("imdbRating") != "N/A":
                    rating = d["imdbRating"]
                if d.get("Genre") and d.get("Genre") != "N/A":
                    genres = [g.strip() for g in d["Genre"].split(",")][:2]
        except Exception:
            pass
    return poster, rating, genres


def get_recommendations(title: str, genre: str, alpha: float):
    try:
        r = requests.get(API_URL, params={"title": title, "alpha": alpha, "genre": genre}, timeout=10)
        return r.json() if r.status_code == 200 else None
    except requests.RequestException:
        return None


def enrich(recs):
    """Fetch OMDb data for all cards in parallel (cache still applies per title)."""
    with ThreadPoolExecutor(max_workers=8) as pool:
        extras = list(pool.map(lambda m: fetch_omdb_data(m["title"]), recs))
    return [{**m, "poster": p, "imdb": r, "genres": g} for m, (p, r, g) in zip(recs, extras)]


def render_grid(recs):
    cards = []
    for i, m in enumerate(recs, 1):
        title = html.escape(str(m["title"]))
        imdb = f'<span class="mm-imdb">★ {html.escape(str(m["imdb"]))}</span>' if m["imdb"] != "N/A" else ""
        chips = "".join(f'<span class="mm-genre">{html.escape(g)}</span>' for g in m["genres"])
        cards.append(f"""
        <div class="mm-card" title="{title}">
          <div class="mm-poster">
            <span class="mm-rank">#{i}</span>{imdb}
            <img src="{html.escape(m['poster'])}" alt="{title} poster" loading="lazy">
          </div>
          <div class="mm-body">
            <div class="mm-title">{title}</div>
            <div class="mm-genres">{chips}</div>
          </div>
        </div>""")
    st.markdown(f'<div class="mm-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- layout
st.markdown('<h1 class="hero-title">MovieMatch AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Hybrid recommendations — <b>content</b> + <b>collaborative</b> signals, fused live.</p>',
            unsafe_allow_html=True)

c1, c2, c3 = st.columns([5, 2, 1.4])
with c1:
    query = st.text_input("Search", placeholder="Search a movie you love — e.g. Inception, Iron Man…",
                          label_visibility="collapsed")
with c2:
    genre = st.selectbox("Genre", GENRES, label_visibility="collapsed")
with c3:
    go = st.button("Recommend", use_container_width=True)

with st.expander("⚙ Tune the blend"):
    alpha = st.slider("Content ↔ Crowd weight (α)", 0.0, 1.0, 0.45, 0.05,
                      help="Higher α = more metadata-driven (plot, cast, genres). "
                           "Lower α = more crowd-driven (MovieLens ratings).")
    st.caption(f"final_score = {alpha:.2f} × content + {1-alpha:.2f} × collaborative")

# ---------------------------------------------------------------- results
# Render unconditionally: Enter in the search box, the button, the genre
# select, and the alpha slider all rerun the script and refresh results live.
with st.spinner("Curating your list…"):
    data = get_recommendations(query.strip(), genre, alpha)

if data is None:
    st.markdown('<div class="mm-note">Couldn\'t reach the recommendation engine. '
                'Start it with <code>python -m uvicorn main:app --reload</code> from the repo root.</div>',
                unsafe_allow_html=True)
else:
    source = data.get("source_movie", "Unknown")
    recs = data.get("recommendations", [])
    message = data.get("message", "")
    cold_start = "Trending" in source or source == "Unknown"

    if cold_start:
        if query.strip():
            st.markdown(f'<div class="mm-note">No match for <b>{html.escape(query)}</b> — '
                        'showing what\'s trending instead.</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-head"><h2>🔥 Trending now</h2>'
                    '<span>rated by the crowd</span></div>', unsafe_allow_html=True)
    else:
        tail = f'top {genre} picks' if genre != "All" else "top picks"
        st.markdown(f'<div class="section-head"><h2>Because you watched '
                    f'<em>{html.escape(source)}</em></h2><span>{tail}</span></div>',
                    unsafe_allow_html=True)

    if not recs:
        st.markdown(f'<div class="mm-note">{html.escape(message) or "No results."}</div>',
                    unsafe_allow_html=True)
    else:
        render_grid(enrich(recs))

st.markdown(
    '<div class="mm-footer">MovieMatch AI · TF-IDF content + item-item CF · '
    'posters &amp; ratings by OMDb</div>',
    unsafe_allow_html=True,
)
