import streamlit as st
import pandas as pd

# Load dataset
@st.cache_data
def load_data():
    ratings = pd.read_csv('u.data', sep='\t', names=['userId', 'movieId', 'rating', 'timestamp'])
    movies = pd.read_csv('u.item', sep='|', encoding='latin-1', header=None, usecols=[0, 1], names=['movieId', 'title'])
    df = ratings.merge(movies, on='movieId')
    return df, movies

df, movies = load_data()

st.title("🎬 Simple Movie Recommender")
st.markdown("Enter a user ID (1 to 943) to get recommendations based on unrated top movies.")

user_id = st.number_input("Enter User ID:", min_value=1, max_value=943, step=1)

if st.button("Recommend Movies"):
    try:
        # Movies rated by the user
        user_rated = df[df['userId'] == user_id]['movieId'].unique()

        # Movies not rated by the user
        unrated_movies = df[~df['movieId'].isin(user_rated)]

        # Average ratings for those movies
        top_unrated = (
            unrated_movies
            .groupby('movieId')
            .agg({'rating': 'mean', 'title': 'first'})
            .sort_values('rating', ascending=False)
            .head(5)
        )

        if not top_unrated.empty:
            st.subheader("📽 Recommended Movies:")
            for _, row in top_unrated.iterrows():
                st.write(f"🎬 **{row['title']}** — Avg Rating: {row['rating']:.2f}")
        else:
            st.error("Could not find unrated movies for this user.")

    except Exception as e:
        st.error(f"Something went wrong: {e}")
