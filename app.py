import streamlit as st
import pickle
import pandas as pd
import requests
import time
import os
import gdown

# -------- DELETE CORRUPTED FILES (IMPORTANT) -------- #
if os.path.exists("movie_dict.pkl"):
    os.remove("movie_dict.pkl")

if os.path.exists("similarity.pkl"):
    os.remove("similarity.pkl")


# -------- DOWNLOAD PKL FILES FROM GOOGLE DRIVE -------- #
def download_file(file_id, file_name):
    url = f"https://drive.google.com/uc?id={file_id}"

    if not os.path.exists(file_name):
        gdown.download(url, file_name, quiet=False)


# 🔥 YOUR GOOGLE DRIVE FILE IDs
download_file("1tnmRHfJ5KccdDce3wsnuQBzVXRvx90yk", "movie_dict.pkl")
download_file("1MYWBXoqCxTF7rajBbRgEvq8LTXHcPrO4", "similarity.pkl")

# -------- SESSION -------- #
session = requests.Session()


# -------- FETCH POSTER -------- #
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"

    for _ in range(3):
        try:
            response = session.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()

                if data.get('poster_path'):
                    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
                else:
                    return "https://via.placeholder.com/500x750?text=No+Image"

        except requests.exceptions.RequestException:
            time.sleep(1)

    return "https://via.placeholder.com/500x750?text=Error"


# -------- LOAD DATA -------- #
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))


# -------- RECOMMEND FUNCTION -------- #
def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]

        movies_list = sorted(
            list(enumerate(distances)),
            reverse=True,
            key=lambda x: x[1]
        )[1:6]

        recommended_movies = []
        recommended_movies_posters = []

        for i in movies_list:
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movies.append(movies.iloc[i[0]].title)

            poster = fetch_poster(movie_id)
            recommended_movies_posters.append(poster)

            time.sleep(0.3)

        return recommended_movies, recommended_movies_posters

    except Exception as e:
        st.error(f"Error: {e}")
        return [], []


# -------- UI -------- #
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox(
    'Select a movie',
    movies['title'].values
)

# -------- BUTTON -------- #
if st.button('Recommend'):

    names, posters = recommend(selected_movie_name)

    if names:
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.text(names[0])
            st.image(posters[0])

        with col2:
            st.text(names[1])
            st.image(posters[1])

        with col3:
            st.text(names[2])
            st.image(posters[2])

        with col4:
            st.text(names[3])
            st.image(posters[3])

        with col5:
            st.text(names[4])
            st.image(posters[4])

    else:
        st.warning("No recommendations found.")