# 🎬 Movie Recommender System

A content-based movie recommendation system that suggests similar movies based on genre, cast, director, and plot keywords using cosine similarity.

## 📌 Overview

This project recommends movies by analyzing each movie's plot overview, genres, keywords, top cast members, and director. It converts this combined information into numerical vectors and calculates similarity between movies using cosine similarity — the higher the similarity score, the more relevant the recommendation.

## 🛠️ Tech Stack

- **Python**
- **Pandas** – data manipulation
- **Scikit-learn** – text vectorization (CountVectorizer) and cosine similarity
- **NLTK** – text stemming
- **Streamlit** – web interface

## 📂 Dataset

[TMDB 5000 Movie Dataset](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata) (Kaggle) — includes movie metadata, genres, keywords, cast, and crew for 4800+ movies.

## ⚙️ How It Works

1. Merged movie metadata with cast/crew data
2. Cleaned and parsed genres, keywords, cast, and crew fields
3. Combined all features into a single `tags` field per movie
4. Applied stemming to normalize words
5. Converted text into vectors using `CountVectorizer` (bag-of-words, top 5000 words)
6. Calculated cosine similarity between all movie vectors
7. Built a function to return the top 5 most similar movies for any given movie

## 🚀 How to Run Locally

1. Clone this repository
```bash
   git clone https://github.com/ujjwal-pandey-14/movie-recommender-system.git
   cd movie-recommender-system
```

2. Install dependencies
```bash
   pip install -r requirements.txt
```

3. Download the dataset (`tmdb_5000_movies.csv` and `tmdb_5000_credits.csv`) from [Kaggle](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata) and place them in the project folder

4. Generate the model files
```bash
   python train_model.py
```

5. Run the app
```bash
   streamlit run app.py
```

## 📸 Demo

*(Add a screenshot of your app here)*

## 🔮 Future Improvements

- Add movie posters using the TMDB API
- Deploy the app online (Streamlit Community Cloud)
- Implement collaborative filtering for personalized recommendations
- Add a search bar with autocomplete instead of a dropdown

## 👤 Author

**Ujjwal Pandey**  
CSE (Data Science), 3rd Year