# 🎬 CineMood

## A Mood-Based Movie Recommendation System

CineMood intelligently recommends movies based on your personal taste profile and current emotional state. By leveraging AI and the TMDB API, it delivers personalized film suggestions that either complement or enhance your mood.

![CineMood](https://img.shields.io/badge/CineMood-Movie%20Recommender-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)
![OpenAI](https://img.shields.io/badge/OpenAI-AI%20Analysis-green)
![TMDB](https://img.shields.io/badge/TMDB-Movie%20Data-yellow)

## ✨ Features

- **🧠 Personality Quiz**: Complete a customized film taste assessment to build your personal profile
- **😊 Mood Analysis**: Select your current emotional state from presets or describe custom moods
- **🎯 Targeted Recommendations**: Receive AI-curated movie suggestions that match both your taste profile and emotional state
- **📺 Streaming Information**: Find out where to watch each recommended movie
- **🖼️ Visual Previews**: View movie posters for recommended films
- **💾 Persistent Profiles**: Your preferences are remembered throughout your session

## 🛠️ Technology Stack

- **Python** - Core application logic
- **Streamlit** - Interactive user interface
- **OpenAI API** - Natural language processing for profile analysis and recommendation generation
- **TMDB API** - Movie database integration for detailed film information and streaming availability
- **dotenv** - Environment variable management for API credentials

## 📋 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/YourUsername/CineMood.git
   ```

2. Navigate to the project directory:
   ```bash
   cd CineMood
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your API credentials:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   TMDB_API_KEY=your_tmdb_api_key_here
   OPEN_AI_MODEL=gpt-4-turbo # or your preferred OpenAI model
   ```

5. Run the application:
   ```bash
   cd midterm
   streamlit run app.py
   ```

## 🚀 Usage

1. **Take the Movie Personality Quiz**:
   - Answer questions about your film preferences
   - Receive a personalized movie taste profile

2. **Select Your Current Mood**:
   - Choose from preset moods or describe a custom one
   - Click "Get Recommendations" to generate suggestions

3. **Explore Recommendations**:
   - View your personalized movie selections with explanations
   - See where each movie is available for streaming
   - Browse movie posters to help with your selection

4. **Start Watching**:
   - Choose a movie and enjoy!
   - Return any time to get new recommendations based on different moods

## 🧩 How It Works

CineMood combines several technologies to create its recommendation system:

1. **User Profile Creation**: The application uses OpenAI to analyze your quiz responses and create a detailed taste profile including preferred genres, themes, and film qualities.

2. **Mood Matching**: Your current emotional state is matched with appropriate film characteristics using AI analysis.

3. **TMDB Integration**: The app searches the TMDB database for movies matching your profile and mood parameters.

4. **AI Curation**: OpenAI analyzes potential matches to select the most appropriate films and generates personalized explanations.

5. **Streaming Availability**: The app checks where each recommended movie can be watched using TMDB's provider data.

## 🔧 Configuration Options

You can customize CineMood by modifying the following:

- **OpenAI Model**: Change the `OPEN_AI_MODEL` in your `.env` file to use different AI capabilities
- **Quiz Questions**: Modify the questions in `MoodMovieRecommender.py` to focus on different aspects of film taste
- **Mood Options**: Add or change mood presets in `app.py` to reflect different emotional states

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgements

- [TMDB API](https://www.themoviedb.org/documentation/api) for movie data
- [OpenAI](https://openai.com/) for AI-powered analysis
- [Streamlit](https://streamlit.io/) for the web interface