import os
import streamlit as st
from sarvamai import SarvamAI
import tempfile
from sarvamai.play import save
# -----------------------------
# Conversation memory
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [] 
    
    if st.button("🧹 Clear Conversation"):
       st.session_state.messages = []
       st.rerun()
# -----------------------------
# Display conversation history
# -----------------------------
chat_container = st.container()

with chat_container:

    for message in st.session_state.messages:

        if message["role"] == "user":

            with st.chat_message("user"):
                st.write(message["content"])

        elif message["role"] == "assistant":

            with st.chat_message("assistant"):
                st.write(message["content"])

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="BhashaSahay",
    page_icon="🇮🇳",
    layout="centered"
)

# -----------------------------
# Sarvam AI setup
# -----------------------------
api_key = os.environ.get("SARVAM_API_SUBSCRIPTION_KEY")

if not api_key:
    st.error("Sarvam API key not found.")
    st.stop()

client = SarvamAI(
    api_subscription_key=api_key
)

# -----------------------------
# BhashaSahay Header
# -----------------------------
st.markdown(
    """
    <div style="text-align: center; padding: 10px 0 20px 0;">
        <h1 style="margin-bottom: 5px;"> BhashaSahay</h1>
        <p style="font-size: 18px; margin-top: 0;">
            Your multilingual AI assistant
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Language selection
# ----------------------------- 
st.markdown("### 🌐 Choose your language")
language = st.selectbox(
    "language",
    [
        "Kannada",
        "Hindi",
        "Tamil",
        "Telugu",
        "Malayalam",
        "Marathi",
        "Bengali",
        "English"
    ]
)
language_codes = {
    "Kannada": "kn-IN",
    "Hindi": "hi-IN",
    "Tamil": "ta-IN",
    "Telugu": "te-IN",
    "Malayalam": "ml-IN",
    "Marathi": "mr-IN",
    "Bengali": "bn-IN",
    "English": "en-IN"
}

language_code = language_codes[language]

# -----------------------------
# Voice input
# -----------------------------
st.markdown("### 🎤 Ask using your voice")
st.caption("Speak naturally in your preferred Indian language.")

audio = st.audio_input("Record your question")

voice_question = ""

if audio:
    st.audio(audio)

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    ) as temp_file:

        temp_file.write(audio.getvalue())
        audio_path = temp_file.name

    with open(audio_path, "rb") as audio_file:

         stt_response = client.speech_to_text.transcribe(
        file=("audio.wav", audio_file, "audio/wav"),
            model="saaras:v4",
            language_code=language_code,
            mode="transcribe"
        )

    voice_question = stt_response.transcript

    st.success("Voice converted to text!")
    st.write(voice_question)

# -----------------------------
# User question
# -----------------------------
question = voice_question

if not question:
    st.markdown("### 💬 Ask BhashaSahay")
    question = st.text_area(
        "What do you need help with?",
        placeholder="Type your question here..."
    )


# -----------------------------
# Ask AI button
# -----------------------------
if st.button("🤖 Ask BhashaSahay"):

    if not question.strip():
        st.warning("Please enter a question first.")

    else:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })
        with st.chat_message("user"):
                    st.write(question)

        messages = [
            {
                "role": "system",
                "content": f"""
You are BhashaSahay, an AI assistant designed to help
people access information easily in Indian languages.

The user's preferred language is {language}.

Answer the user's questions in {language}.

Use simple language.
Avoid unnecessary technical terms.
Understand the context of previous messages.

If the user asks a follow-up question, use the previous
conversation to understand what they are referring to.
"""
            }
        ]

        messages.extend(st.session_state.messages)

        with st.spinner("BhashaSahay is thinking..."):

            response = client.chat.completions(
                model="sarvam-105b",
                messages=messages
            )

        answer = response.choices[0].message.content

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

        with st.chat_message("assistant", avatar="🇮🇳"):
             st.markdown("### 🇮🇳 BhashaSahay")
             st.write(answer)

        # -----------------------------
        # AI Voice Response
        # -----------------------------
        with st.spinner("🔊 Preparing voice response..."):

            if answer and answer.strip():

                audio_response = client.text_to_speech.convert(
                    text=answer,
                    language_code=language_code,
                    model="bulbul:v3",
                    speaker="shubh"
                )

                audio_file = "bhashasahay_response.wav"

                save(audio_response, audio_file)

                st.audio(audio_file)

            else:
                st.warning(
                    "Voice response could not be generated because the AI answer was empty."
                )