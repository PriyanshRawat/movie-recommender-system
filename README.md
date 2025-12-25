# 🎬 MovieMatch AI
### Hybrid Movie Recommendation System

MovieMatch AI is a **full-stack machine learning application** that delivers personalized movie recommendations using a **Hybrid Recommendation Architecture**. It combines **Content-Based Filtering** (movie metadata & NLP) with **Collaborative Filtering** (user–item interactions) to produce accurate, explainable, and cold-start–aware recommendations.

---

## ✨ Key Features

- **🧠 Hybrid Recommendation Engine**  
  Combines semantic similarity (overview, genres, cast, keywords) with collaborative user behavior.

- **🔍 Robust Fuzzy Search**  
  Uses `TheFuzz` to tolerate typos and partial queries (e.g. `shawshank redeption → The Shawshank Redemption`).

- **📉 Cold Start Handling**  
  Automatically falls back to a popularity-based recommender when user or movie history is unavailable.

- **⚡ High-Performance Backend**  
  FastAPI backend with preloaded artifacts and sub-200ms inference.

- **🎨 Interactive Frontend**  
  Streamlit-based UI with live movie posters via OMDb API.

- **⚡ Smart Caching**  
  TTL-based caching to reduce API calls and improve latency.

---

## 🛠️ Tech Stack

**Data & ML**
- Pandas, NumPy
- Scikit-Learn (TF-IDF / CountVectorizer, Cosine Similarity)

**Backend**
- FastAPI, Uvicorn

**Frontend**
- Streamlit

**External APIs**
- OMDb API (movie posters)

**Utilities**
- TheFuzz (fuzzy string matching)
- python-dotenv (environment management)

---

## ⚙️ How It Works

MovieMatch AI uses a **late-fusion hybrid recommender**.

### 1️⃣ Content-Based Model
- NLP over movie overview, genres, keywords, cast, and director
- Vectorization using TF-IDF / CountVectorizer
- Similarity computed via cosine similarity

### 2️⃣ Collaborative Filtering Model
- Item–item similarity using MovieLens ratings
- Mean-centered ratings to capture like/dislike signals

### 3️⃣ Hybrid Scoring Formula

$$
FinalScore = \alpha \times ContentScore + (1 - \alpha) \times CollaborativeScore
$$

- `α` is tunable (default: `0.45`)
- Higher α → semantic similarity
- Lower α → crowd preference

---

## 📂 Project Structure

```text
├── artifacts/                  # Generated model artifacts (ignored by Git)
│   ├── movies_df.pkl
│   ├── similarity.pkl
│   ├── movie_similarity.npy
│   ├── tmdb_to_ml.pkl
│   ├── trending.pkl
│   └── movie_idx_lookup.pkl
│
├── data/                       # Raw datasets (ignored by Git)
├── model_generation.ipynb      # Training & artifact generation
├── main.py                     # FastAPI backend
├── frontend.py                 # Streamlit frontend
├── requirements.txt            # Python dependencies
├── .env                        # API keys (ignored by Git)
└── README.md
```

---

## ▶️ Running the Application

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/PriyanshRawat/movie-recommender-system.git
cd movie-recommender-system
```

---

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Data Setup (Required for Training)

Download datasets from Kaggle:

- **[TMDB 5000 Movie Dataset](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata)**  
  `tmdb_5000_movies.csv`, `tmdb_5000_credits.csv`

- **[MovieLens Latest Small](https://www.kaggle.com/datasets/shubhammehta21/movie-lens-small-latest-dataset)** 
  `ratings.csv`, `links.csv`

Place all files into:

```text
data/
```

---

### 4️⃣ Generate Model Artifacts

Artifacts are not stored on GitHub due to size.

```bash
jupyter notebook movie_recommender_system.ipynb
```

Run all cells and confirm `artifacts/` is populated.

---

### 5️⃣ Configure Environment Variables

Create a `.env` file:

```env
OMDB_API_KEY=your_actual_api_key_here
```

Get a free key from https://www.omdbapi.com/

---

### 6️⃣ Start the Backend

```bash
python -m uvicorn main:app --reload
```

Backend runs at:

```text
http://127.0.0.1:8000
```

---

### 7️⃣ Start the Frontend

```bash
python -m streamlit run frontend.py
```

Frontend opens at:

```text
http://localhost:8501
```

---

## 🔮 Future Improvements

- [ ] Dockerization
- [ ] Neural Collaborative Filtering
- [ ] User authentication & profiles
- [ ] Diversity-aware re-ranking
- [ ] Online feedback loop

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a Pull Request

---

## 👤 Author

**Priyansh Rawat**

If you find this project useful, consider giving it a ⭐ on GitHub.

