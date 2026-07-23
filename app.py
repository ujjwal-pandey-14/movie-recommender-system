import streamlit as st
import pickle

# Load the saved model files
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# App title
st.title('Movie Recommender System')

# Dropdown to select a movie
selected_movie = st.selectbox(
    'Select a movie to get recommendations:',
    movies['title'].values
)

# Recommend function
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommended_movies = []
    for i in movies_list:
        recommended_movies.append(movies.iloc[i[0]].title)
    return recommended_movies

# Button and output
if st.button('Recommend'):
    recommendations = recommend(selected_movie)
    for movie in recommendations:
        st.write(movie)