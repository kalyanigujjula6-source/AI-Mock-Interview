# 🤖 AI-Powered Mock Interview & Evaluation System

An AI-powered mock interview application that helps students and job seekers practice interviews and receive instant AI-based feedback.

## 🚀 Features

- 🤖 AI-generated interview questions
- 🎤 Voice-based answer recording
- 📝 Text-based answers
- 🗣️ Speech-to-text conversion
- 🧠 AI-based answer evaluation
- 📊 Technical, Communication and Relevance scores
- ✅ Correct answer for wrong/incomplete responses
- 💡 Better interview-quality answer
- 📚 Personalized improvement suggestions
- 📈 Final interview performance report
- 🎯 Career recommendation

## 🛠️ Technologies Used

- Python 3.11
- Streamlit
- Google Gemini AI
- SpeechRecognition
- PyAudio
- Pandas
- NumPy
- Scikit-learn
- spaCy
- NLTK
- Transformers
- PyTorch

## 🔄 System Workflow

Candidate  
↓  
Streamlit User Interface  
↓  
AI Question Generation  
↓  
Text / Voice Answer  
↓  
Speech-to-Text  
↓  
AI Answer Evaluation  
↓  
Scores & Feedback  
↓  
Correct Answer + Better Answer  
↓  
Final Performance Report

## 💻 Requirements

- Windows 10/11
- Python 3.11+
- Microphone
- Speakers or Headphones
- Internet connection
- Gemini API key

## ▶️ How to Run

1. Clone or download this repository.
2. Create and activate a Python virtual environment.
3. Install the required packages:

```bash
pip install -r requirements.txt
Create a `.env` file and add your Gemini API key.

GEMINI_API_KEY=your_api_key_here
 Run the application:

streamlit run app.py
