import streamlit as st
import pickle
import pandas as pd
import requests
import time
import os
import gdown

# -------- DOWNLOAD FILES ONLY IF NOT EXISTS -------- #
def download_file(file_id, file_name):
    if not os.path.exists(file_name):
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, file_name, quiet=False)

# 🔥 FILE IDs
download_file("1tnmRHfJ5KccdDce3wsnuQBzVXRvx90yk", "movie_dict.pkl")
download_file("1MYWBXoqCxTF7rajBbRgEvq8LTXHcPrO4", "similarity.pkl")


# -------- CACHE DATA (VERY IMPORTANT) -------- #
@st.cache_resource
def load_data():
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies, similarity

movies, similarity = load_data()


# -------- SESSION -------- #
session = requests.Session()

@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"

    try:
        response = session.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('poster_path'):
                return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    except:
        pass

    return "https://via.placeholder.com/500x750?text=No+Image"


# -------- RECOMMEND FUNCTION -------- #
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    names = []
    posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        names.append(movies.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))

    return names, posters


# -------- UI -------- #
st.title("🎬 Movie Recommender System")

selected_movie_name = st.selectbox(
    "Select a movie",
    movies['title'].values
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i])