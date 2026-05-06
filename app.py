# import streamlit as st
# import pickle
# import pandas as pd
# import requests
#
# def fetch_poster(movie_id):
#     response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US'.format(movie_id))
#     data = response.json()
#     print(data)
#     return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
#
# def recommend(movie):
#     movie_index = movies[movies['title'] == movie].index[0]
#     distances = similarity[movie_index]
#     movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
#     recommended_movies = []
#     recommended_movies_posters = []
#     for i in movies_list:
#         movie_id = movies.iloc[i[0]].movie_id
#         recommended_movies.append(movies.iloc[i[0]].title)
#         recommended_movies_posters.append(fetch_poster(movie_id))
#     return recommended_movies, recommended_movies_posters
#
# movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
# movies = pd.DataFrame(movies_dict)
# similarity = pickle.load(open('similarity.pkl', 'rb'))
# st.title('Movie Recommender System')
#
# selected_movie_name = st.selectbox(
#     'Select a movie',
#     movies['title'].values
# )
#
# if st.button('Recommend'):
#     names, posters = recommend(selected_movie_name)
#
#     col1, col2, col3, col4, col5 = st.columns(5)
#     with col1:
#         st.text(names[0])
#         st.image(posters[0])
#     with col2:
#         st.text(names[1])
#         st.image(posters[1])
#     with col3:
#         st.text(names[2])
#         st.image(posters[2])
#     with col4:
#         st.text(names[3])
#         st.image(posters[3])
#     with col5:
#         st.text(names[4])
#         st.image(posters[4])
#
#
# #8265bd1679663a7ea12ac168da84d2e8
# #https://api.themoviedb.org/3/movie/{movie_id}?api_key=<<api_key>>&language=en-US



import streamlit as st
import pickle
import pandas as pd
import requests
import time

# -------- SESSION (connection reuse) -------- #
session = requests.Session()

# -------- FETCH POSTER (with retry + cache) -------- #
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"

    for attempt in range(3):  # retry 3 times
        try:
            response = session.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()

                if data.get('poster_path'):
                    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
                else:
                    return "https://via.placeholder.com/500x750?text=No+Image"

        except requests.exceptions.RequestException as e:
            print(f"Retry {attempt+1} failed:", e)
            time.sleep(1)

    return "https://via.placeholder.com/500x750?text=Error"


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

            time.sleep(0.3)  # prevent API overload

        return recommended_movies, recommended_movies_posters

    except Exception as e:
        st.error(f"Error: {e}")
        return [], []


# -------- LOAD DATA -------- #
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))

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