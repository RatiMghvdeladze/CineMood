import os
import json
import random
import openai
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPEN_AI_MODEL = os.getenv("OPEN_AI_MODEL")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")  # Add this to your .env file


class MoodMovieRecommender:
    def __init__(self):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPEN_AI_MODEL
        self.tmdb_api_key = TMDB_API_KEY
        self.tmdb_base_url = "https://api.themoviedb.org/3"
        self.user_profile = {}
        self.quiz_results = {}
        self.current_mood = ""

    def run_personality_quiz(self):
        """Run a film taste quiz to understand user preferences"""
        questions = [
            "Do you prefer action-packed movies or slow-paced character studies?",
            "Do you enjoy movies with happy endings or prefer more realistic/ambiguous endings?",
            "Name three of your favorite movies of all time.",
            "Do you like movies that make you think, or ones that are pure entertainment?",
            "Do you prefer classic films or modern cinema?",
            "Are there any genres you absolutely avoid watching?",
            "Do you enjoy foreign language films?",
            "Do you prefer to watch movies alone or with others?"
        ]

        answers = {}
        print("\n--- MOVIE PERSONALITY QUIZ ---")
        for i, question in enumerate(questions, 1):
            print(f"\nQuestion {i}: {question}")
            answer = input("Your answer: ")
            answers[f"q{i}"] = answer

        # Process quiz results with AI
        self._analyze_quiz_results(answers)
        return self.quiz_results

    def _analyze_quiz_results(self, answers):
        """Use AI to analyze quiz answers and create a user profile"""
        answers_text = "\n".join([f"Q: {k}: {v}" for k, v in answers.items()])

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a film expert who can analyze a person's movie preferences. "
                                              "Create a detailed profile of their film taste based on their quiz answers. "
                                              "Include their preferred genres, themes, and film qualities. "
                                              "Structure your response as a JSON object with these keys: "
                                              "preferred_genres (list of TMDB genre IDs and names), "
                                              "disliked_genres (list of TMDB genre IDs and names), "
                                              "tone_preferences (list), narrative_style (string), "
                                              "decade_preference (string), and viewing_context (string). "
                                              "Use proper TMDB genre IDs: Action (28), Adventure (12), Animation (16), "
                                              "Comedy (35), Crime (80), Documentary (99), Drama (18), Family (10751), "
                                              "Fantasy (14), History (36), Horror (27), Music (10402), Mystery (9648), "
                                              "Romance (10749), Science Fiction (878), TV Movie (10770), Thriller (53), "
                                              "War (10752), Western (37)."},
                {"role": "user", "content": f"Here are my answers to the movie preference quiz:\n{answers_text}"}
            ]
        )

        # Extract and parse the JSON profile
        try:
            profile_text = response.choices[0].message.content
            # Extract JSON portion if it's embedded in other text
            if '{' in profile_text and '}' in profile_text:
                start = profile_text.find('{')
                end = profile_text.rfind('}') + 1
                profile_text = profile_text[start:end]

            self.user_profile = json.loads(profile_text)

            # Create a human-readable summary of the profile
            self.quiz_results = self._create_profile_summary()
        except json.JSONDecodeError:
            print("Error parsing AI response. Using simplified profile.")
            # Fallback to a simpler format if JSON parsing fails
            self.user_profile = {
                "preferred_genres": [{"id": 18, "name": "Drama"}, {"id": 35, "name": "Comedy"}],
                "disliked_genres": [],
                "tone_preferences": ["uplifting"],
                "narrative_style": "character-driven",
                "decade_preference": "modern",
                "viewing_context": "social"
            }
            self.quiz_results = self._create_profile_summary()

    def _create_profile_summary(self):
        """Create a human-readable summary of the user profile"""
        profile_prompt = f"""
        Create a friendly, conversational summary of this movie taste profile:
        {json.dumps(self.user_profile)}

        Make it personal and engaging, as if you're talking to the person directly.
        Keep it to 3-4 sentences maximum.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system",
                 "content": "You are a friendly film enthusiast who can summarize people's movie preferences in an engaging way."},
                {"role": "user", "content": profile_prompt}
            ]
        )

        return response.choices[0].message.content

    def get_current_mood(self):
        """Ask the user about their current mood"""
        print("\n--- HOW ARE YOU FEELING TODAY? ---")
        print("Examples: happy, sad, stressed, relaxed, bored, energetic, thoughtful, nostalgic...")
        self.current_mood = input("Your current mood: ").strip().lower()
        return self.current_mood

    def get_tmdb_genre_ids(self):
        """Get genre IDs from the user profile"""
        genre_ids = []
        try:
            for genre in self.user_profile["preferred_genres"]:
                if isinstance(genre, dict) and "id" in genre:
                    genre_ids.append(genre["id"])
                elif isinstance(genre, str):
                    # Try to map common genre names to IDs
                    genre_map = {
                        "action": 28, "adventure": 12, "animation": 16, "comedy": 35,
                        "crime": 80, "documentary": 99, "drama": 18, "family": 10751,
                        "fantasy": 14, "history": 36, "horror": 27, "music": 10402,
                        "mystery": 9648, "romance": 10749, "sci-fi": 878, "science fiction": 878,
                        "tv movie": 10770, "thriller": 53, "war": 10752, "western": 37
                    }
                    if genre.lower() in genre_map:
                        genre_ids.append(genre_map[genre.lower()])
        except (KeyError, TypeError):
            # Fallback to some popular genres if we can't extract from profile
            genre_ids = [18, 35, 28]  # Drama, Comedy, Action

        return genre_ids

    def search_tmdb_movies(self, mood, page=1):
        """Search for movies using TMDB API based on genre preferences"""
        genre_ids = self.get_tmdb_genre_ids()
        genre_param = ",".join(map(str, genre_ids[:3]))  # Use up to 3 genres

        # Map mood to sort options
        mood_to_sort = {
            "happy": "popularity.desc",
            "sad": "vote_average.desc",
            "relaxed": "vote_average.desc",
            "excited": "popularity.desc",
            "thoughtful": "vote_count.desc",
            "nostalgic": "primary_release_date.asc",
            # Add more mood mappings as needed
        }

        # Default sort by popularity
        sort_by = mood_to_sort.get(self.current_mood.lower(), "popularity.desc")

        # Determine release year range based on decade_preference
        year_filter = ""
        if "decade_preference" in self.user_profile:
            if "modern" in self.user_profile["decade_preference"].lower():
                year_filter = "&primary_release_date.gte=2010-01-01"
            elif "classic" in self.user_profile["decade_preference"].lower():
                year_filter = "&primary_release_date.lte=1989-12-31"
            elif "90s" in self.user_profile["decade_preference"].lower():
                year_filter = "&primary_release_date.gte=1990-01-01&primary_release_date.lte=1999-12-31"
            # Add more decade filters as needed

        # Construct the API endpoint
        endpoint = f"{self.tmdb_base_url}/discover/movie"
        params = f"?api_key={self.tmdb_api_key}&with_genres={genre_param}&sort_by={sort_by}&page={page}&vote_count.gte=100{year_filter}"

        try:
            response = requests.get(endpoint + params)
            response.raise_for_status()  # Raise exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to TMDB API: {e}")
            return {"results": []}

    def get_movie_details(self, movie_id):
        """Get detailed information about a specific movie"""
        endpoint = f"{self.tmdb_base_url}/movie/{movie_id}"
        params = f"?api_key={self.tmdb_api_key}&append_to_response=credits"

        try:
            response = requests.get(endpoint + params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting movie details: {e}")
            return {}

    def get_movie_providers(self, movie_id):
        """Get streaming providers for a specific movie"""
        endpoint = f"{self.tmdb_base_url}/movie/{movie_id}/watch/providers"
        params = f"?api_key={self.tmdb_api_key}"

        try:
            response = requests.get(endpoint + params)
            response.raise_for_status()
            data = response.json()
            # Return US providers if available, otherwise empty dict
            if "results" in data and "US" in data["results"]:
                return data["results"]["US"]
            return {}
        except requests.exceptions.RequestException as e:
            print(f"Error getting movie providers: {e}")
            return {}

    def recommend_movies(self):
        """Generate movie recommendations based on user profile and current mood"""
        if not self.user_profile or not self.current_mood:
            return "Please complete the personality quiz and share your mood first."

        # Get mood-based movie recommendations from TMDB
        movies_data = self.search_tmdb_movies(self.current_mood)

        # If we didn't get enough results, try another page
        if len(movies_data.get("results", [])) < 5:
            more_movies = self.search_tmdb_movies(self.current_mood, page=2)
            movies_data["results"] = movies_data.get("results", []) + more_movies.get("results", [])

        # Get up to 10 movies to analyze
        movie_candidates = movies_data.get("results", [])[:10]

        if not movie_candidates:
            return "No movies found that match your preferences. Please try a different mood."

        # Get detailed information for each movie
        detailed_movies = []
        for movie in movie_candidates:
            details = self.get_movie_details(movie["id"])
            if details:
                # Extract director
                director = "Unknown"
                if "credits" in details and "crew" in details["credits"]:
                    for crew_member in details["credits"]["crew"]:
                        if crew_member["job"] == "Director":
                            director = crew_member["name"]
                            break

                detailed_movies.append({
                    "id": details["id"],
                    "title": details["title"],
                    "year": details["release_date"][:4] if "release_date" in details else "Unknown",
                    "director": director,
                    "overview": details["overview"],
                    "genres": [genre["name"] for genre in details.get("genres", [])],
                    "vote_average": details.get("vote_average", 0),
                    "popularity": details.get("popularity", 0)
                })

        # Use AI to select the best matches for the current mood
        if detailed_movies:
            return self._analyze_movies_for_mood(detailed_movies)
        else:
            return "Couldn't retrieve detailed movie information. Please try again later."

    def _analyze_movies_for_mood(self, detailed_movies):
        """Use AI to select and explain the best movies for the current mood"""
        # Store detailed_movies as an instance attribute so it's available in get_streaming_availability
        self.detailed_movies = detailed_movies

        movies_json = json.dumps(detailed_movies)

        recommendation_prompt = f"""
        Based on this user's movie taste profile:
        {json.dumps(self.user_profile)}

        And their current mood: {self.current_mood}

        And this list of candidate movies from TMDB:
        {movies_json}

        Select the 5 movies that would best match both their taste profile and current mood.
        For each movie, include:
        1. Title (Year)
        2. Director
        3. A brief explanation of why this movie matches both their taste profile and current mood

        Format your response as a numbered list.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system",
                 "content": "You are an expert film recommender with encyclopedic knowledge of cinema."},
                {"role": "user", "content": recommendation_prompt}
            ]
        )

        recommendations = response.choices[0].message.content

        # Store the recommended movie IDs for streaming lookup
        self.recommended_movie_ids = []
        for movie in detailed_movies:
            if movie["title"] in recommendations:
                self.recommended_movie_ids.append(movie["id"])

        return recommendations

    def get_streaming_availability(self, recommendations):
        """Check where the recommended movies are available for streaming using TMDB data"""
        if not hasattr(self, "recommended_movie_ids") or not self.recommended_movie_ids:
            # Extract movie titles from recommendations text
            import re
            movie_titles = re.findall(r'\d+\.\s+([^(]+)', recommendations)

            streaming_prompt = f"""
            For these recommended movies:

            {recommendations}

            Suggest where each might be available for streaming (Netflix, Hulu, Amazon Prime, Disney+, HBO Max, etc.).
            If you're not certain, make your best educated guess based on the type of film and its age/popularity.

            Format your response as a simple list showing "Movie Title - Likely available on: [services]" for each movie.
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system",
                     "content": "You are a helpful assistant with knowledge about movie streaming availability."},
                    {"role": "user", "content": streaming_prompt}
                ]
            )

            return response.choices[0].message.content

        # If we have movie IDs, look up actual streaming info
        streaming_info = []
        for movie_id in self.recommended_movie_ids:
            providers = self.get_movie_providers(movie_id)

            # Get movie title
            movie_title = ""
            # We need to use self.detailed_movies which is stored during recommend_movies
            if hasattr(self, "detailed_movies"):
                for movie in self.detailed_movies:
                    if movie["id"] == movie_id:
                        movie_title = movie["title"]
                        break

            # If we still don't have a title, fetch it directly
            if not movie_title:
                try:
                    details = self.get_movie_details(movie_id)
                    movie_title = details.get("title", f"Movie {movie_id}")
                except:
                    movie_title = f"Movie {movie_id}"

            # Extract provider names
            available_on = []

            # Check flatrate (subscription) providers
            if "flatrate" in providers:
                for provider in providers["flatrate"]:
                    available_on.append(provider["provider_name"])

            # Check rent providers if no subscription options
            if not available_on and "rent" in providers:
                for provider in providers["rent"][:3]:  # Limit to 3 rental options
                    available_on.append(f"{provider['provider_name']} (rent)")

            # Format the provider information
            if available_on:
                provider_text = ", ".join(available_on)
                streaming_info.append(f"{movie_title} - Available on: {provider_text}")
            else:
                streaming_info.append(f"{movie_title} - No streaming data available")

        if streaming_info:
            return "\n".join(streaming_info)
        else:
            # Fallback to AI-generated suggestions
            return self.get_streaming_availability(recommendations)  # This will use the AI fallback

    def run_full_workflow(self):
        """Run the complete movie recommendation workflow"""
        print("Welcome to the Mood-Based Movie Recommender!")
        print("Let's start by understanding your movie preferences.")

        # Run personality quiz
        profile = self.run_personality_quiz()
        print("\n--- YOUR MOVIE PERSONALITY ---")
        print(profile)

        # Get current mood
        mood = self.get_current_mood()
        print(f"\nFeeling {mood}? Let's find some movies for you!")

        # Generate recommendations
        print("\n--- YOUR PERSONALIZED RECOMMENDATIONS ---")
        recommendations = self.recommend_movies()
        print(recommendations)

        # Get streaming availability
        print("\n--- WHERE TO WATCH ---")
        streaming_info = self.get_streaming_availability(recommendations)
        print(streaming_info)

        return {
            "profile": profile,
            "mood": mood,
            "recommendations": recommendations,
            "streaming_info": streaming_info
        }


if __name__ == "__main__":
    recommender = MoodMovieRecommender()
    results = recommender.run_full_workflow()