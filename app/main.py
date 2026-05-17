
import streamlit as st
from Services.text_extraction import extract_text_from_pdf
from core.exceptions import PDFExtractionError
from core.config import VOICE_OPTION
import requests

st.set_page_config(
    page_title="PDF To Podcast AI",
    page_icon="🎙️",
    layout="centered"
)
st.title("Fantasto Bargh", text_alignment= "center")
st.subheader("Welcomes you",  text_alignment= "center")
st.write("Turn study materials, research papers, Text and documents into AI-generated podcast episodes.")
select_model = st.selectbox("Select Model", VOICE_OPTION)

tab_podcast, tab_audio_podcast = st.tabs(["🎙️ PDF To Podcast", "✍️ Text to Speech"])

with tab_audio_podcast:

    user_input = st.text_area("Enter your prompt")
    

    if st.button("Send"):
        if not user_input.strip():
            st.error("Please Enter the Text.")

        else:
            try:
                response = requests.post("http://127.0.0.1:8000/generate-text-to-speech", json={"text": user_input, "model": select_model})
                if response.status_code != 200:
                    st.error(response.json()["detail"])
                    st.stop()
                audio_bytes = response.content

            except Exception as e:
                st.error("Something unexpected went wrong. Please try again.")
                st.stop()

            if audio_bytes is not None:
                st.subheader("Download Audio")

                st.audio(audio_bytes)

                st.success("Audio Generated Successfully!")

                st.download_button(
                    label="Download",
                    data = audio_bytes,
                    file_name="Fantasto-Bargh_audio.mp3",
                    mime="audio/mp3"
                )


with tab_podcast:
    uploaded_file = st.file_uploader(
    "Upload a PDF",
    type=["pdf"]
    )
    if uploaded_file:

        try:
            extracted_text = extract_text_from_pdf(uploaded_file)
        except PDFExtractionError as e:
            st.error(f"Error in Extracting Texts From PDF. {e}")
            st.stop()

        if st.button("Generate AI Podcast"):

            try:
                response = requests.post("http://127.0.0.1:8000/generate-pdf-to-podcast", json={"text": extracted_text, "model": select_model})
                if response.status_code != 200:
                    st.error(response.json()["detail"])
                    st.stop()
                audio_bytes2 = response.content

            except Exception as e:
                st.error("Something unexpected went wrong. Please try again.")
                st.stop()
                

            if audio_bytes2 is not None:
                
                st.subheader("Download Audio")
                st.audio(audio_bytes2)
                st.success("Podcast Generated Successfully!")
                st.download_button(
                    label="Download",
                    data=audio_bytes2,
                    file_name="Fantasto-Bargh_podcast_audio.mp3",
                    mime="audio/mp3"
                )

st.write("Made with ❤️ by Fantasto Bargh")
