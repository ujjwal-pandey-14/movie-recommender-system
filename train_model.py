import pandas as pd
import ast
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.porter import PorterStemmer

# Load raw data
movies = pd.read_csv('tmdb_5000_movies.csv')
credits = pd.read_csv('tmdb_5000_credits.csv')

movies = movies.merge(credits, on='title')

# Standardize movie_id
if 'id' in movies.columns and 'movie_id' not in movies.columns:
    movies.rename(columns={'id': 'movie_id'}, inplace=True)

# Keep raw fields before transforming for tags
movies['raw_overview'] = movies['overview'].fillna('')
movies['vote_average'] = movies['vote_average'].fillna(0.0)
movies['release_date'] = movies['release_date'].fillna('')
movies['runtime'] = movies['runtime'].fillna(0)

def extract_names(text):
    if not isinstance(text, str):
        return []
    try:
        L = []
        for i in ast.literal_eval(text):
            L.append(i['name'])
        return L
    except Exception:
        return []

movies['genre_list'] = movies['genres'].apply(extract_names)

movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew', 'raw_overview', 'vote_average', 'release_date', 'runtime', 'genre_list']]
movies.dropna(subset=['overview', 'genres', 'keywords', 'cast', 'crew'], inplace=True)

def convert(text):
    L = []
    for i in ast.literal_eval(text):
        L.append(i['name'])
    return L

def convert_cast(text):
    L = []
    counter = 0
    for i in ast.literal_eval(text):
        if counter < 3:
            L.append(i['name'])
            counter += 1
        else:
            break
    return L

def fetch_director(text):
    L = []
    for i in ast.literal_eval(text):
        if i['job'] == 'Director':
            L.append(i['name'])
            break
    return L

processed_genres = movies['genres'].apply(convert)
keywords = movies['keywords'].apply(convert)
cast = movies['cast'].apply(convert_cast)
crew = movies['crew'].apply(fetch_director)
overview_split = movies['overview'].apply(lambda x: str(x).split())

pg_clean = processed_genres.apply(lambda x: [i.replace(" ", "") for i in x])
kw_clean = keywords.apply(lambda x: [i.replace(" ", "") for i in x])
c_clean = cast.apply(lambda x: [i.replace(" ", "") for i in x])
cr_clean = crew.apply(lambda x: [i.replace(" ", "") for i in x])

movies['tags'] = overview_split + pg_clean + kw_clean + c_clean + cr_clean

new_df = movies[['movie_id', 'title', 'tags', 'raw_overview', 'vote_average', 'release_date', 'runtime', 'genre_list']].copy()
new_df.rename(columns={'raw_overview': 'overview'}, inplace=True)
new_df['tags'] = new_df['tags'].apply(lambda x: " ".join(x))
new_df['tags'] = new_df['tags'].apply(lambda x: x.lower())

ps = PorterStemmer()
def stem(text):
    y = []
    for i in text.split():
        y.append(ps.stem(i))
    return " ".join(y)

new_df['tags'] = new_df['tags'].apply(stem)

cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(new_df['tags']).toarray()

similarity = cosine_similarity(vectors)

pickle.dump(new_df, open('movies.pkl', 'wb'))
pickle.dump(similarity, open('similarity.pkl', 'wb'))

print("Model files generated successfully with rich metadata!")