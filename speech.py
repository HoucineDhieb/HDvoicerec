import streamlit as st
import speech_recognition as sr
import assemblyai as aai
import os


def transcribe_speech(api_choice, language, audio_file=None):
    # Initialize recognizer class
    r = sr.Recognizer()
    if api_choice == 'Google':
        is_paused = False
        with sr.Microphone() as source:
            st.info("Speak now (press 'Pause' to stop recording):")
            while not is_paused:
                st.session_state.pause = st.button("Pause")
                if st.session_state.get("pause"):
                    is_paused = True
            st.spinner("Listening...")
            audio_text = r.listen(source)

        st.info("Transcribing...")
        try:
            # Using Google Speech Recognition
            text = r.recognize_google(audio_text, language=language)
            return text

        except sr.UnknownValueError:
            return "Sorry, the speech was not understood."
        except sr.RequestError as e:
            return f"Google API error: {str(e)}"

    elif api_choice == 'AssemblyAI' and audio_file:
        try:
            aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
            if not aai.settings.api_key:
                raise ValueError("AssemblyAI API key not found in environment variables.")

            transcriber = aai.Transcriber()
            st.info("Uploading audio file to AssemblyAI...")
            transcript = transcriber.transcribe(audio_file)
            text = transcript.get("text", "Transcription failed or empty.")
            return text
        except Exception as e:
            return f"AssemblyAI error: {str(e)}"

    return "Invalid option or no audio file provided."


def main():
    # Set up AssemblyAI API key from environment or Streamlit settings
    os.environ["ASSEMBLYAI_API_KEY"] = st.secrets.get("ASSEMBLYAI_API_KEY", "")

    # Set up Streamlit page
    st.set_page_config(page_title="Speech Recognition App", layout="wide")
    st.title("Speech Recognition App")
    st.write("Click on the microphone or upload audio to start transcribing.")

    # API Choice and Settings
    st.subheader("Settings")
    api_choice = st.selectbox("Select API:", ["Google", "AssemblyAI"])
    language = st.text_input("Specify Language (e.g., 'en-US')", value="en-US")
    save_transcription = st.checkbox("Save transcription?")

    # File Uploader for AssemblyAI
    st.subheader("Audio Input")
    audio_file = None
    upload_audio = st.file_uploader("Upload audio file (AssemblyAI only):", type=["mp3", "wav", "flac"])
    if upload_audio:
        audio_file = upload_audio.name
        with open(audio_file, "wb") as f:
            f.write(upload_audio.getbuffer())

    # Start Transcription
    if st.button("Start Transcription"):
        text = transcribe_speech(api_choice, language, audio_file)
        st.success("Transcription completed!")
        st.write("Transcription: ", text)

        if save_transcription:
            with open("transcription.txt", "w") as f:
                f.write(text)
            st.info("Transcription saved to 'transcription.txt'")


if __name__ == "__main__":
    main()
