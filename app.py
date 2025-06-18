# app.py

import streamlit as st
import pandas as pd
from surprise import Dataset, Reader, KNNBasic
from surprise.model_selection import train_test_split

# Load dataset
@st.cache_data
def load_data():
    ratings = pd.read_csv('u.data', sep='\t', names=['userId', 'movieId', 'rating', 'timestamp'])
    movies = pd.read_csv('u.item', sep='|', encoding='latin-1', header=None, usecols=[0, 1], names=['movieId', 'title'])
    movies['movieId'] = movies['movieId'].astype(int)
    data = ratings.merge(movies, on='movieId')
    return data, movies

data, movies = load_data()

# Train collaborative filtering model
@st.cache_resource
def train_model(data):
    reader = Reader(rating_scale=(1, 5))
    dataset = Dataset.load_from_df(data[['userId', 'movieId', 'rating']], reader)
    trainset = dataset.build_full_trainset()
    sim_options = {'name': 'cosine', 'user_based': True}
    model = KNNBasic(sim_options=sim_options)
    model.fit(trainset)
    return model

model = train_model(data)

# App UI
st.title("🎬 Movie Recommender App")
st.markdown("Enter a user ID (1 to 943) to get movie recommendations:")

# Input from user
user_id = st.number_input("User ID:", min_value=1, max_value=943, step=1)

# When button is clicked
if st.button("Get Recommendations"):
    try:
        rated_movie_ids = data[data['userId'] == user_id]['movieId'].tolist()
        all_movie_ids = movies['movieId'].tolist()
        unrated_ids = [mid for mid in all_movie_ids if mid not in rated_movie_ids]

        # Predict ratings
        predictions = [model.predict(user_id, mid) for mid in unrated_ids]
        top_n = sorted(predictions, key=lambda x: x.est, reverse=True)[:5]

        # Show results
        st.subheader("📽 Recommended Movies:")
        for pred in top_n:
            title = movies[movies['movieId'] == pred.iid]['title'].values[0]
            st.write(f"🎬 **{title}** — Predicted Rating: {pred.est:.2f}")

    except Exception as e:
        st.error(f"Something went wrong: {e}")
