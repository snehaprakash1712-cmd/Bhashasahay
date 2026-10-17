import os
import tempfile
import streamlit as st
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

# -----------------------------
# Conversation memory
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if st.button("🧹 Clear Conversation"):
    st.session_state.messages = []
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