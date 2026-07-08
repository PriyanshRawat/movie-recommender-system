# 🎬 MovieMatch AI
### Hybrid Movie Recommendation System

MovieMatch AI is a **full-stack machine learning application** that delivers personalized movie recommendations using a **Hybrid Recommendation Architecture**. It combines **Content-Based Filtering** (movie metadata & NLP) with **Collaborative Filtering** (user–item interactions) to produce accurate, explainable, and cold-start–aware recommendations.

The whole stack is **Dockerized** .

---

## ✨ Key Features

- **🧠 Hybrid Recommendation Engine**  
  Combines semantic similarity (overview, genres, cast, keywords) with collaborative user behavior.

- **🔍 Robust Fuzzy Search**  
  Two-stage title resolution: a normalized exact match (`spiderman → Spider-Man`), then `TheFuzz` token-sort matching for typos (`shawshank redeption → The Shawshank Redemption`).

- **📉 Cold Start Handling**  
  Automatically falls back to a popularity-based recommender when the movie is unknown or the search box is empty.

- **⚡ High-Performance Backend**  
  FastAPI backend with artifacts preloaded once at startup and sub-200ms inference.

- **🛡️ Hardened API**  
  Rate limiting (30 req/min per IP via SlowAPI), CORS allow-list, query validation, and fail-fast artifact loading.

- **🎨 Two Interchangeable Frontends**  
  `frontend_v2.py` (cinematic dark redesign, the default) and `frontend.py` (original) — same backend, same API, different look.

- **⭐ IMDb Ratings & Posters**  
  Enriched from the OMDb API; `frontend_v2.py` also renders genre chips and parallelizes lookups.

- **⚡ Smart Caching**  
  TTL-based caching to reduce API calls and improve latency.

- **🐳 Containerized**  
  Prebuilt backend and frontend images published on Docker Hub — pull and run, no build step.

---

## 🛠️ Tech Stack

**Data & ML**
- Pandas, NumPy
- Scikit-Learn (TF-IDF, Cosine Similarity)
- NLTK (Porter stemming)

**Backend**
- FastAPI, Uvicorn
- SlowAPI (rate limiting)

**Frontend**
- Streamlit

**External APIs**
- OMDb API (movie posters, IMDb ratings, genres)

**Infrastructure**
- Docker (images on [Docker Hub](https://hub.docker.com/repositories/priyanshrawat))
- Git LFS (model artifacts)

**Utilities**
- TheFuzz (fuzzy string matching)
- python-dotenv (environment management)

---

## ⚙️ How It Works

MovieMatch AI uses a **late-fusion hybrid recommender**. Both similarity matrices are built offline in the
notebook and fused at request time.

### 1️⃣ Content-Based Model
- NLP over movie overview, genres, keywords, cast, and director (genres + director weighted ×2)
- Porter stemming, then vectorization with `TfidfVectorizer(max_features=5000)`
- Similarity computed via cosine similarity

### 2️⃣ Collaborative Filtering Model
- Item–item similarity using MovieLens ratings
- Mean-centered ratings to capture like/dislike signals
- TMDB ↔ MovieLens IDs bridged via lookup tables; movies with no MovieLens counterpart simply contribute no CF signal

### 3️⃣ Hybrid Scoring Formula

$$
FinalScore = \alpha \times ContentScore + (1 - \alpha) \times CollaborativeScore
$$

- `α` is tunable (default: `0.45`)
- Higher α → semantic similarity
- Lower α → crowd preference

---

## 🔌 API

A single endpoint, served at `http://127.0.0.1:8000`:

```text
GET /recommend?title=Inception&alpha=0.45&genre=Action
```

| Parameter | Default | Notes |
|---|---|---|
| `title` | `""` | Empty or unmatched → trending cold-start list |
| `alpha` | `0.45` | Content weight, clamped to `[0, 1]` |
| `genre` | `All` | Post-filters the candidate set |

Returns the top 10 recommendations as `{ source_movie, recommendations[] }`. Rate limited to 30 requests/minute per IP.

---

## 📂 Project Structure

```text
├── artifacts/                          # Model artifacts (tracked via Git LFS)
│   ├── movies_df.pkl
│   ├── similarity.pkl
│   ├── movie_similarity.npy
│   ├── tmdb_to_ml.pkl
│   ├── movie_id_search.pkl
│   └── trending.pkl
│
├── data/                               # Raw datasets (ignored by Git)
├── movie_recommender_completed.ipynb   # Training & artifact generation
├── main.py                             # FastAPI backend
├── frontend_v2.py                      # Streamlit frontend (default, cinematic redesign)
├── frontend.py                         # Streamlit frontend (original)
├── Dockerfile.backend                  # Backend image
├── Dockerfile.frontend                 # Frontend image (serves frontend_v2.py)
├── docker-compose.yml                  # Build both images from source
├── docker-compose.deploy.yml           # Run the prebuilt Docker Hub images
├── requirements.txt                    # Python dependencies
├── .env                                # API keys (ignored by Git)
└── README.md
```

---

## 🐳 Run with Docker (Recommended)

No clone, no Python, no dataset download. Both images are published on Docker Hub:

- **Backend** → [`priyanshrawat/movie-recommender-backend`](https://hub.docker.com/r/priyanshrawat/movie-recommender-backend) — FastAPI + trained artifacts baked in
- **Frontend** → [`priyanshrawat/movie-recommender-frontend`](https://hub.docker.com/r/priyanshrawat/movie-recommender-frontend) — Streamlit, serves `frontend_v2.py`

### 1️⃣ Pull the Images

```bash
docker pull priyanshrawat/movie-recommender-backend:latest
docker pull priyanshrawat/movie-recommender-frontend:latest
```

---

### 2️⃣ Create a Network

The frontend reaches the backend by container name, so both must share a network.

```bash
docker network create moviematch
```

---

### 3️⃣ Run Both Containers

```bash
docker run -d --name backend --network moviematch -p 8000:8000 \
  priyanshrawat/movie-recommender-backend:latest

docker run -d --name frontend --network moviematch -p 8501:8501 \
  -e API_URL=http://backend:8000/recommend \
  -e OMDB_API_KEY=your_actual_api_key_here \
  priyanshrawat/movie-recommender-frontend:latest
```

Open **http://localhost:8501**.

- The container **must** be named `backend` — that hostname is what `API_URL` resolves.
- `OMDB_API_KEY` is optional; without it you get placeholder posters, no ratings, and no genre chips. Free key at https://www.omdbapi.com/
- On Windows PowerShell, replace the trailing `\` line continuations with backticks (`` ` ``) or put each command on one line.

---

### 4️⃣ Tear Down

```bash
docker rm -f frontend backend
docker network rm moviematch
```

---

## 🧑‍💻 Running from Source

### 1️⃣ Clone the Repository

Artifacts are stored with **Git LFS**, so install it before cloning — otherwise you get pointer files instead of models.

```bash
git lfs install
git clone https://github.com/PriyanshRawat/movie-recommender-system.git
cd movie-recommender-system
```

---

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Configure Environment Variables

Create a `.env` file in the repo root:

```env
OMDB_API_KEY=your_actual_api_key_here
```

Get a free key from https://www.omdbapi.com/

Without a key the app still runs — you just get placeholder posters and no ratings.

---

### 4️⃣ Start the Backend

Launch from the **repo root** — artifacts are loaded via relative paths.

```bash
python -m uvicorn main:app --reload
```

Backend runs at:

```text
http://127.0.0.1:8000
```

---

### 5️⃣ Start the Frontend

In a second terminal:

```bash
python -m streamlit run frontend_v2.py                  # -> http://localhost:8501
```

`frontend_v2.py` is the default UI. The original frontend is still available and talks to the same
backend — run it on another port if you want both up at once:

```bash
python -m streamlit run frontend.py --server.port 8502  # -> http://localhost:8502
```

---

> 💡 If you cloned the repo and would rather build the images yourself than pull them,
> `docker compose up --build` does exactly that.

---

## 🔬 Regenerating Model Artifacts

Only needed if you want to retrain — a normal LFS clone already ships the artifacts.

**Download the datasets from Kaggle:**

- **[TMDB 5000 Movie Dataset](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata)**  
  `tmdb_5000_movies.csv`, `tmdb_5000_credits.csv`

- **[MovieLens Latest Small](https://www.kaggle.com/datasets/shubhammehta21/movie-lens-small-latest-dataset)**  
  `ratings.csv`, `links.csv`

Place all four files into `data/`, then run every cell of:

```bash
jupyter notebook movie_recommender_completed.ipynb
```

The notebook writes the `.pkl` / `.npy` files to the **repo root** — move them into `artifacts/` afterwards.

> ⚠️ The content matrix is indexed by **row position** in `movies_df`. If you change the preprocessing, keep the
> row order of the DataFrame and the similarity matrix aligned, or recommendations will silently point at the wrong movies.

---

## 🔮 Future Improvements

- [ ] Neural Collaborative Filtering
- [ ] User authentication & profiles
- [ ] Diversity-aware re-ranking
- [ ] Online feedback loop
- [ ] Backend-side poster caching (`poster_lookup` is currently unused)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a Pull Request

---

## 👤 Author

**Priyansh Rawat**

If you find this project useful, consider giving it a ⭐ on GitHub.
