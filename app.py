import streamlit as st
from openai import OpenAI
import os
import yaml
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader
import tempfile  # For handling uploaded audio files
from pydub import AudioSegment  # To convert audio formats if needed

st.set_page_config(
    page_title="Blender",
    page_icon="✍️",
    layout="centered",
    initial_sidebar_state="auto",
)


with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

authenticator.login()

if st.session_state["authentication_status"]:
    authenticator.logout(location='sidebar')
    st.write(f'Welcome *{st.session_state["name"]}* 👋')
    client = OpenAI()
    client.api_key = os.getenv("OPENAI_API_KEY")

    def Summarize_text(prompt, system_content):


        completion = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        return completion

    def transcribe_audio(audio_file):
        # Convert audio to a compatible format (e.g., WAV)
        audio = AudioSegment.from_file(audio_file)
        temp_wav_path = audio_file + ".wav"
        audio.export(temp_wav_path, format="wav")  # Save as WAV

        with open(temp_wav_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=file
            )

        # Clean up temporary WAV file
        os.remove(temp_wav_path)

        # Return the transcription text using dot notation
        return transcription.text

    def main():
        st.title("Blender - lecture summary AI")
        prompt = st.text_input("Enter prompt or questions", help="This prompt will be specific to this article.")

        uploaded_file = st.file_uploader("Upload a text file", type=["txt"])
        if uploaded_file is not None:
            uploaded_text = uploaded_file.read().decode("utf-8")
            prompt += "\n\n" + uploaded_text

        uploaded_audio = st.file_uploader("Upload an audio file", type=["mp3", "wav", "m4a"])
        if uploaded_audio:
            with tempfile.NamedTemporaryFile(delete=False) as temp_audio_file:
                temp_audio_file.write(uploaded_audio.read())
                temp_audio_path = temp_audio_file.name

            # Convert to WAV if necessary (e.g., for compatibility)
            audio = AudioSegment.from_file(temp_audio_path)
            if uploaded_audio.name.endswith(".mp3") or uploaded_audio.name.endswith(".m4a"):
                temp_audio_path = temp_audio_path.replace(".mp3", ".wav").replace(".m4a", ".wav")
                audio.export(temp_audio_path, format="wav")

            with st.spinner("Transcribing audio..."):
                transcribed_text = transcribe_audio(temp_audio_path)
            st.text_area("Transcribed Text", transcribed_text, height=150)
            prompt += "\n\n" + transcribed_text


        edit_system_content = st.checkbox("Edit System Content", help="This is the default system prompt. Edits will only be applied to this article.")
        default_system_content = "Default system prompt."
        if edit_system_content:
            system_content = st.text_area("System Content", default_system_content, height=400)
        else:
            system_content = default_system_content

        if "response_text" not in st.session_state:
            st.session_state["response_text"] = ""

        generate_summary_button = st.button("Generate Summary")

        output_container = st.container()

        if generate_summary_button:
            st.write("Generating...")
            loading_placeholder = st.empty()
            completion = Summarize_text(prompt, system_content)
            response_text = completion.choices[0].message.content

            loading_placeholder.empty()

            if response_text:
                st.download_button(
                    label="Download Summary",
                    data=response_text.encode("utf-8"),
                    file_name="summary.txt",
                    mime="text/plain"
                )
            else:
                st.write("No summary generated. Please try again.")

            st.session_state["response_text"] = response_text

            with output_container:
                output_container.empty()
                st.write(response_text)

        else:
            with output_container:
                output_container.empty()
                if st.session_state["response_text"]:
                    st.write(st.session_state["response_text"])

    if __name__ == "__main__":
        main()

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')

