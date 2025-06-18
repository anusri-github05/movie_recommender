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

# App UI
st.title("🎬 Simple Movie Recommender")
st.markdown("Enter a user ID (1 to 943) to get recommendations based on similar users.")

user_id = st.number_input("Enter User ID:", min_value=1, max_value=943, step=1)

# Recommendation logic
if st.button("Recommend Movies"):
    try:
        # Movies already rated by user
        user_ratings = df[df['userId'] == user_id]

        # Find other users who rated the same movies
        similar_users = df[df['movieId'].isin(user_ratings['movieId']) & (df['userId'] != user_id)]

        # Recommend movies similar users liked that this user hasn't rated
        top_movies = (
            similar_users[~similar_users['movieId'].isin(user_ratings['movieId'])]
            .groupby('movieId')
            .agg({'rating': 'mean', 'title': 'first'})
            .sort_values('rating', ascending=False)
            .head(5)
        )

        # Display results
        if not top_movies.empty:
            st.subheader("📽 Recommended Movies:")
            for _, row in top_movies.iterrows():
                st.write(f"🎬 **{row['title']}** — Avg Rating: {row['rating']:.2f}")
        else:
            st.warning("No personalized recommendations found for this user. Showing top-rated movies instead.")
            fallback = (
                df.groupby('movieId')
                  .agg({'rating': 'mean', 'title': 'first'})
                  .sort_values('rating', ascending=False)
                  .head(5)
            )
            for _, row in fallback.iterrows():
                st.write(f"🎬 **{row['title']}** — Avg Rating: {row['rating']:.2f}")

    except Exception as e:
        st.error(f"Something went wrong: {e}")
