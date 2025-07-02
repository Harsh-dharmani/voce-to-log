import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import os
from playsound import playsound
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from openai import OpenAI

# --- SETUP ---

# OpenAI API setup using new client
client = OpenAI(api_key="sk-ijklmnopqrstuvwxijklmnopqrstuvwxijklmnop")# Replace with your OpenAI key

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client_sheet = gspread.authorize(creds)
sheet = client_sheet.open("Voice Chat Log").sheet1

# --- FUNCTIONS ---

# Transcribe voice to text
def transcribe_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Listening...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand your voice."
    except sr.RequestError:
        return "Speech recognition service error."

# Get GPT response using new API format
def get_gpt_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error with GPT: {str(e)}"

# Convert text to speech and play it
def speak_text(text):
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    playsound("response.mp3")
    os.remove("response.mp3")

# Log user and bot messages to Google Sheet
def log_to_sheet(user_text, bot_reply):
    sheet.append_row([user_text, bot_reply])

# --- STREAMLIT APP ---

st.set_page_config(page_title="Crystal Voice AI", page_icon="🧠")
st.title("🎤 Crystal Voice AI Demo")
st.markdown("Talk to the AI via voice — it replies and logs your conversation!")

if st.button("Start Talking"):
    user_input = transcribe_audio()
    st.success(f"🗣️ You said: {user_input}")

    bot_response = get_gpt_response(user_input)
    st.info(f"🤖 AI replied: {bot_response}")

    speak_text(bot_response)
    log_to_sheet(user_input, bot_response)
    st.success("✅ Conversation logged to Google Sheet.")
