import requests
import streamlit as st

from MoodMovieRecommender import MoodMovieRecommender

st.set_page_config(page_title="Mood-Based Movie Recommender", page_icon="🎬")

st.title("🎬 Mood-Based Movie Recommender")
st.write("Discover movies that match your taste and current mood!")

# Check for API keys
import os
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("TMDB_API_KEY"):
    st.error("⚠️ TMDB API key not found. Please add it to your .env file as TMDB_API_KEY=your_key_here")
    st.stop()

if not os.getenv("OPENAI_API_KEY"):
    st.error("⚠️ OpenAI API key not found. Please add it to your .env file as OPENAI_API_KEY=your_key_here")
    st.stop()


# Initialize the recommender
@st.cache_resource
def get_recommender():
    return MoodMovieRecommender()


recommender = get_recommender()

# App state
if 'quiz_completed' not in st.session_state:
    st.session_state.quiz_completed = False
if 'profile' not in st.session_state:
    st.session_state.profile = None
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None
if 'streaming_info' not in st.session_state:
    st.session_state.streaming_info = None

# Quiz section
if not st.session_state.quiz_completed:
    st.header("Movie Personality Quiz")
    st.write("Let's start by understanding your movie preferences.")

    with st.form(key="quiz_form"):
        q1 = st.text_input("1. Do you prefer action-packed movies or slow-paced character studies?")
        q2 = st.text_input("2. Do you enjoy movies with happy endings or prefer more realistic/ambiguous endings?")
        q3 = st.text_input("3. Name three of your favorite movies of all time.")
        q4 = st.text_input("4. Do you like movies that make you think, or ones that are pure entertainment?")
        q5 = st.text_input("5. Do you prefer classic films or modern cinema?")
        q6 = st.text_input("6. Are there any genres you absolutely avoid watching?")
        q7 = st.text_input("7. Do you enjoy foreign language films?")
        q8 = st.text_input("8. Do you prefer to watch movies alone or with others?")

        submit_button = st.form_submit_button(label="Submit Quiz")

        if submit_button:
            answers = {
                "q1": q1, "q2": q2, "q3": q3, "q4": q4,
                "q5": q5, "q6": q6, "q7": q7, "q8": q8
            }

            with st.spinner("Analyzing your movie personality..."):
                recommender._analyze_quiz_results(answers)
                st.session_state.profile = recommender.quiz_results
                st.session_state.quiz_completed = True
            st.rerun()

# Mood and recommendations section
else:
    # Display profile
    st.header("Your Movie Personality")
    st.write(st.session_state.profile)

    # Reset button
    if st.button("Retake Quiz"):
        st.session_state.quiz_completed = False
        st.session_state.profile = None
        st.session_state.recommendations = None
        st.session_state.streaming_info = None
        st.experimental_rerun()

    # Mood input
    st.header("How are you feeling today?")
    mood_options = ["Happy", "Sad", "Relaxed", "Excited", "Bored", "Stressed", "Thoughtful", "Nostalgic", "Other"]
    selected_mood = st.selectbox("Select your mood", mood_options)

    if selected_mood == "Other":
        custom_mood = st.text_input("Describe your mood")
        mood = custom_mood if custom_mood else "neutral"
    else:
        mood = selected_mood

    if st.button("Get Recommendations") and mood:
        with st.spinner("Finding perfect movies for your mood using TMDB data..."):
            recommender.current_mood = mood

            # Generate recommendations
            recommendations = recommender.recommend_movies()
            st.session_state.recommendations = recommendations

            # Get streaming availability
            streaming_info = recommender.get_streaming_availability(recommendations)
            st.session_state.streaming_info = streaming_info

    # Display recommendations if available
    if st.session_state.recommendations:
        st.header("Your Personalized Recommendations")
        st.write(st.session_state.recommendations)

        st.header("Where to Watch")
        st.write(st.session_state.streaming_info)

        # Add posters for visual appeal if we have movie IDs
        if hasattr(recommender, "recommended_movie_ids") and recommender.recommended_movie_ids:
            st.header("Movie Posters")
            cols = st.columns(min(5, len(recommender.recommended_movie_ids)))

            for i, movie_id in enumerate(recommender.recommended_movie_ids[:5]):
                poster_path = None
                response = requests.get(
                    f"{recommender.tmdb_base_url}/movie/{movie_id}?api_key={recommender.tmdb_api_key}"
                )
                if response.status_code == 200:
                    movie_data = response.json()
                    if "poster_path" in movie_data and movie_data["poster_path"]:
                        poster_path = f"https://image.tmdb.org/t/p/w500{movie_data['poster_path']}"

                with cols[i]:
                    if poster_path:
                        st.image(poster_path, width=150)
                    else:
                        st.write("No poster available")