# **🎬 CineMatch AI: Hybrid Movie Recommendation System**

**CineMatch AI** is a full-stack machine learning application that provides personalized movie recommendations. It solves the "Cold Start" problem by utilizing a **Hybrid Filtering Architecture**, combining Content-Based Filtering (Tag/Genre analysis) with Collaborative Filtering (User-Item Interaction).

## **📸 Demo**

*(Replace this line with a screenshot of your Streamlit Dashboard)*

## **✨ Key Features**

* **🧠 Hybrid Recommendation Engine:** Fuses metadata similarity (Plot, Genres, Cast) with user voting patterns to provide accurate suggestions.  
* **🔍 Robust Fuzzy Search:** Implements TheFuzz logic to handle typos, partial queries, and misspellings (e.g., "shawshank redeption" → "The Shawshank Redemption").  
* **📉 Cold Start Handling:** Automatically detects new users or unknown queries and falls back to a weighted "Trending Movies" algorithm.  
* **⚡ High-Performance Backend:** Built on **FastAPI** with artifact caching for \<200ms inference time.  
* **🎨 Interactive Frontend:** A modern, responsive UI built with **Streamlit**, featuring real-time movie posters via the **OMDb API**.  
* **⚡ Smart Caching:** Implements TTL-based caching to minimize API calls and latency.

## **🛠️ Tech Stack**

* **Data Processing:** Pandas, NumPy, Scikit-Learn (Cosine Similarity, CountVectorizer)  
* **Backend API:** FastAPI, Uvicorn  
* **Frontend UI:** Streamlit  
* **External API:** OMDb (Open Movie Database) for poster fetching  
* **Utilities:** TheFuzz (String matching), Python-Dotenv

## **⚙️ How It Works (The Logic)**

The system uses a weighted average of two distinct models:

1. **Content-Based Model:**  
   * Uses **Natural Language Processing (NLP)** on movie tags, genres, and overviews.  
   * Vectorizes text data using CountVectorizer.  
   * Calculates similarity using **Cosine Distance**.  
2. **Collaborative Filtering Model:**  
   * Constructs a **User-Item Matrix** from thousands of user ratings.  
   * Identifies voting patterns between movies based on user behavior.  
3. The Hybrid Formula:  
   $$FinalScore \= \\alpha \\times (ContentScore) \+ (1 \- \\alpha) \\times (CollaborativeScore)$$  
   * *Alpha (*$\\alpha$*)* is a tunable hyperparameter (default: 0.45) allowing the user to balance between "Content Similarity" and "User Trends".

## **📂 Project Structure**

├── artifacts/             \# Generated model files (Ignored by Git)  
│   ├── movies\_df.pkl      \# Processed Metadata  
│   ├── similarity.pkl     \# Content Similarity Matrix  
│   ├── trending.pkl       \# Top rated movies for fallback  
│   └── ...  
├── artifacts\_generation.ipynb  \# Notebook to train models & generate artifacts  
├── main.py                \# FastAPI Backend Application  
├── frontend.py            \# Streamlit Frontend Interface  
├── requirements.txt       \# Python Dependencies  
├── .env                   \# API Keys (Ignored by Git)  
└── README.md              \# Project Documentation

## **🚀 Installation & Setup**

### **1\. Clone the Repository**

git clone \[https://github.com/YOUR\_USERNAME/movie-recommender-system.git\](https://github.com/YOUR\_USERNAME/movie-recommender-system.git)  
cd movie-recommender-system

### **2\. Install Dependencies**

pip install \-r requirements.txt

### **3\. Generate Model Artifacts (Crucial\!)**

Because the similarity matrices are large, they are not stored on GitHub. You must generate them locally.

* Open Untitled5 (1).ipynb (or rename it to model\_generation.ipynb).  
* **Run all cells.**  
* Ensure the artifacts/ folder is created and populated with .pkl and .npy files.

### **4\. Configure Environment Variables**

Create a file named .env in the root directory and add your OMDb API key:

OMDB\_API\_KEY=your\_actual\_api\_key\_here

*(Get a free key at [omdbapi.com](http://www.omdbapi.com/apikey.aspx))*

## **🏃‍♂️ How to Run**

You need to run the Backend and Frontend in separate terminals.

**Terminal 1: Start Backend**

python \-m uvicorn main:app \--reload

*The API will start at http://127.0.0.1:8000*

**Terminal 2: Start Frontend**

python \-m streamlit run frontend.py

*The App will open in your browser at http://localhost:8501*

## **🔮 Future Improvements**

* \[ \] Dockerize the application for easier deployment.  
* \[ \] Implement Deep Learning (Neural Collaborative Filtering).  
* \[ \] Add User Authentication to save personal watchlists.

## **🤝 Contributing**

Contributions are welcome\! Please fork the repo and submit a Pull Request.

Author: \[Your Name\]  
Connect: \[Your LinkedIn/GitHub Link\]