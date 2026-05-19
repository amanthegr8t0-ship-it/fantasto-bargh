
import streamlit as st
from core.config import VOICE_OPTION, FASTAPI_URL
import requests
import time

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
                status_text = st.empty()
                response = requests.post(f"{FASTAPI_URL}/generate-text-to-speech", json={"text": user_input, "model": select_model})
                if response.status_code != 200:
                    st.error(response.json()["detail"])
                    st.stop()
                job_id = response.json()["job_id"]
                count = 0
                while True:
                    counter = count%3
                    status_response = requests.get(f"{FASTAPI_URL}/job/tts/{job_id}")
                    # status_text.write(f"Status code: {status_response.status_code}")

                    if status_response.headers["content-type"] == "audio/mpeg":
                        status_text.write("Status : Completed")
                        audio_bytes = status_response.content
                        break

                    status = status_response.json()["status"]
                    status_text.write(f"Status : {status}"+int(counter)*".")
                    time.sleep(3)
                    count += 1

            except Exception as e:
                st.error(f"Error: {type(e).__name__}: {str(e)}")
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
            status_text2 = st.empty()
            response = requests.post(f"{FASTAPI_URL}/extract-pdf-text", files={"file": uploaded_file})
            if response.status_code != 200:
                st.error(response.json()["detail"])
                st.stop()
            extracted_text = response.text
        except Exception as e:
            st.error("Error during text extraction from pdf")
            st.stop()

        if st.button("Generate AI Podcast"):

            try:
                response = requests.post(f"{FASTAPI_URL}/generate-pdf-to-podcast", json={"text": extracted_text, "model": select_model})
                if response.status_code != 200:
                    st.error(response.json()["detail"])
                    st.stop()
                job_id2 = response.json()["job_id"]
                count = 0
                while True:
                    counter = count%3
                    status_response = requests.get(f"{FASTAPI_URL}/job/podcast/{job_id2}")

                    if status_response.headers["content-type"] == "audio/mpeg":
                        status_text2.write("Status : Completed")
                        audio_bytes2 = status_response.content
                        break

                    status = status_response.json()["status"]
                    status_text2.write(f"Status : {status}"+int(counter)*".")
                    time.sleep(3)
                    count += 1

            except Exception as e:
                st.error(f"Something unexpected went wrong. Please try again. {e}")
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
