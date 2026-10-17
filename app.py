import os
import json
import tempfile
import streamlit as st
from datetime import datetime
from pypdf import PdfReader
from sarvamai import SarvamAI
from sarvamai.play import save

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="BhashaSahay",
    page_icon="🇮🇳",
    layout="centered"
)
st.markdown("""
<style>
/* Main page */
.stApp {
    background: linear-gradient(135deg, #f5f7ff 0%, #f7fbff 55%, #f2fbf8 100%);
}

.block-container {
    max-width: 1000px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Headings */
h1 {
    color: #26356b !important;
    font-weight: 800 !important;
    letter-spacing: -1px;
}

h2, h3 {
    color: #344477 !important;
    font-weight: 700 !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #4f46e5, #6366f1);
    color: white !important;
    border: none;
    border-radius: 12px;
    padding: 0.55rem 1.1rem;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: #3730a3;
    border: none;
    color: white !important;
}

/* Input fields and selectors */
div[data-baseweb="select"] > div,
.stTextArea textarea,
.stTextInput input {
    border-radius: 10px;
}

/* Subtle separation between sections */
div[data-testid="stFileUploader"],
div[data-testid="stAudioInput"] {
    border-radius: 12px;
}

/* Keep content readable */
p, label {
    line-height: 1.6;
}
/* Lighter, cleaner input fields */
div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #26356b !important;
    border: 1px solid #d8def0 !important;
}

div[data-baseweb="select"] * {
    color: #26356b !important;
}

.stTextArea textarea,
.stTextInput input {
    background-color: #ffffff !important;
    color: #26356b !important;
    border: 1px solid #d8def0 !important;
}

div[data-testid="stFileUploader"] {
    background: #ffffff;
    border: 1px solid #e0e6f5;
    border-radius: 14px;
    padding: 12px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Conversation memory
# -----------------------------
HISTORY_FILE = "conversation_history.json"


def load_conversation_history():
    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            history = json.load(file)
            return history if isinstance(history, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_conversation_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(history, file, ensure_ascii=False, indent=2)
    except OSError as error:
        st.warning(f"Could not save conversation history: {error}")


if "messages" not in st.session_state:
    st.session_state.messages = load_conversation_history()


if st.button("🧹 Clear Conversation"):
    st.session_state.messages = []
    save_conversation_history([])
    st.rerun()
# -----------------------------
# Sarvam AI setup
# -----------------------------
api_key = os.environ.get("SARVAM_API_SUBSCRIPTION_KEY")

if not api_key:
    st.error("Sarvam API key not found. Check your API key settings.")
    st.stop()

client = SarvamAI(api_subscription_key=api_key)

# -----------------------------
# BhashaSahay header
# -----------------------------
st.markdown(
    """
    <div style="text-align: center; padding: 10px 0 20px 0;">
        <h1 style="margin-bottom: 5px;">BhashaSahay</h1>
        <p style="font-size: 18px; margin-top: 0;">
            Your multilingual AI assistant
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.info(
    "👋 Namaste! Ask questions in your preferred Indian language, "
    "translate text, study from PDF notes, or speak naturally using your voice."
)
# -----------------------------
# Choose mode
# -----------------------------
st.markdown("### ✨ Choose your mode")

mode = st.selectbox(
    "What would you like to do?",
    ["Normal Chat", "Translation", "Study Assistant"],
    key="assistant_mode"
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
# PDF document understanding
# -----------------------------
st.markdown("### 📄 Understand Your Documents")
st.caption(
    "Upload your study notes or a PDF and ask questions "
    "in your preferred language."
)

uploaded_pdf = st.file_uploader(
    "Upload a PDF document",
    type=["pdf"],
    key="document_uploader"
)

document_text = ""

if uploaded_pdf is not None:
    try:
        pdf_reader = PdfReader(uploaded_pdf)

        document_text = "\n".join(
            page.extract_text() or ""
            for page in pdf_reader.pages
        )

        if document_text.strip():
            st.success("PDF uploaded and read successfully!")

            with st.expander("Preview document text"):
                st.write(document_text[:3000])
        else:
            st.warning(
                "No readable text found. This PDF may contain scanned images."
            )

    except Exception as error:
        st.error(f"Could not read the PDF: {error}")

# -----------------------------
# Voice input
# -----------------------------
st.markdown("### 🎤 Ask using your voice")
st.caption("Speak naturally in your preferred Indian language.")

audio = st.audio_input("Record your question")
voice_question = ""

if audio is not None:
    st.audio(audio)

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav"
        ) as temp_file:
            temp_file.write(audio.getvalue())
            audio_path = temp_file.name

        try:
            with open(audio_path, "rb") as audio_file:
                stt_response = client.speech_to_text.transcribe(
                    file=("audio.wav", audio_file, "audio/wav"),
                    model="saaras:v4",
                    language_code=language_code,
                    mode="transcribe"
                )

            voice_question = stt_response.transcript

        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)

        if voice_question:
            st.success("Voice converted to text!")
            st.write(voice_question)

    except Exception as error:
        st.error(f"Voice transcription failed: {error}")

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
# Display previous conversation
# -----------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# -----------------------------
# Ask AI button
# -----------------------------
if st.button("🤖 Ask BhashaSahay"):

    if not question or not question.strip():
        st.warning("Please enter a question first.")

    else:
        # Add the user's message to conversation history
        st.session_state.messages.append({
            "role": "user",
            "content": question.strip()
        })
        save_conversation_history(st.session_state.messages)

        # Base instructions
        system_prompt = f"""
You are BhashaSahay, a helpful multilingual AI assistant.

The user's preferred language is {language}.
Answer in {language}, using simple, natural language.
Avoid unnecessary technical terms.
Understand follow-up questions using the conversation history.

If a PDF document is provided, use its content to answer
questions about that document:

{document_text[:15000]}

If the answer is not in the PDF, clearly say so.
Do not invent information from the document.
If no PDF is uploaded, answer general questions normally.
"""

        # Mode-specific instructions
        if mode == "Translation":
           system_prompt += f"""
TRANSLATION MODE — STRICT RULES:
- Translate the user's input into {language}.
- Translate the exact text only.
- Do not answer questions or respond conversationally.
- Do not add advice, greetings, wishes, explanations, or extra sentences.
- Preserve the original meaning.
- Output only the translated text.
"""



        elif mode == "Study Assistant":
            system_prompt += f"""

STUDY ASSISTANT MODE:
Help the user understand study topics and prepare for exams.
Explain concepts step by step in simple {language}.
Use clear definitions and exam-friendly points.
When appropriate, help with revision and practice questions.
"""

        # Create messages INSIDE the button, before using them
        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

        messages.extend(st.session_state.messages)

        try:
            with st.spinner("BhashaSahay is thinking..."):
                response = client.chat.completions(
                    model="sarvam-105b",
                    messages=messages
                )

                answer = response.choices[0].message.content

            if not answer or not answer.strip():
                st.error("BhashaSahay returned an empty answer.")

            else:
                # Save assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })
                save_conversation_history(st.session_state.messages)

                with st.chat_message("assistant", avatar="🇮🇳"):
                    st.markdown("### 🇮🇳 BhashaSahay")
                    st.write(answer)

                # -----------------------------
                # AI voice response
                # -----------------------------
                try:
                    with st.spinner("🔊 Preparing voice response..."):
                        audio_response = client.text_to_speech.convert(
                            text=answer,
                            language_code=language_code,
                            model="bulbul:v3",
                            speaker="shubh"
                        )

                        audio_file = "bhashasahay_response.wav"
                        save(audio_response, audio_file)

                    st.audio(audio_file)

                except Exception as error:
                    st.warning(
                        f"Text answer is ready, but voice generation failed: {error}"
                    )

        except Exception as error:
            st.error(f"BhashaSahay could not answer: {error}")