import streamlit as st
from openai import OpenAI
import os
import yaml
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader

st.set_page_config(
    page_title="Juicer",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="auto",
)


logo_img = "logo.png"
st.image(logo_img, width=50)

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
    client.api_key = st.secrets["OPENAI_API_KEY"]
    # client.api_key = os.getenv("OPENAI_API_KEY")

    def Summarize_text(prompt, model_name, system_content):
        if model_name == "gpt-4-turbo-2024-04-09" or "gpt-4o-2024-05-13":
            max_tokens = 4096
        else:
            max_tokens = 6000

        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens
        )
        return completion

    def main():
        st.title("Juicer - Strategy Writer.")
        prompt = st.text_input("Enter prompt or questions", help="This prompt will be specific to this article.")

        uploaded_file = st.file_uploader("Upload a text file", type=["txt"])
        if uploaded_file is not None:
            uploaded_text = uploaded_file.read().decode("utf-8")
            prompt += "\n\n" + uploaded_text

        models = ["gpt-4-turbo-2024-04-09", "gpt-3.5-turbo-16k", "gpt-4o-2024-05-13"]
        model_name = st.selectbox("Select the model", models)

        edit_system_content = st.checkbox("Edit System Content", help="This is the default system prompt. Edits will only be applied to this article")
        default_system_content = """
        When I give you a podcast transcription, with style after a British business coach, begin each Strategy Smoothie by identifying the key question or problem a business owner might be considering, to help entrepreneurs quickly determine if the strategy discussed fits their current needs. delves into key strategies extracted from interviews, offering practical insights.

explore a primary strategy in detail, include additional relevant strategies when beneficial, and provide a summary of its application along with three detailed steps for practical implementation. give Recommendations for further reading and practical tools are included, making the advice practical and relevant for a global audience of college-educated entrepreneurs. 
The conversational tone, akin to advice from a seasoned coach, makes complex strategies accessible and engaging.

Include useful resources e.g. books, tech stack tools, podcasts
"""
        if edit_system_content:
            system_content = st.text_area("System Content ", default_system_content, height=400)
        else:
            system_content = default_system_content

        if "response_text_juicer" not in st.session_state:
            st.session_state["response_text_juicer"] = ""

        generate_summary_button = st.button("Generate Summary")

        output_container = st.container()

        if generate_summary_button:
            st.write("Generating...")
            loading_placeholder = st.empty()
            completion = Summarize_text(prompt, model_name, system_content)
            response_text_juicer = completion.choices[0].message.content

            loading_placeholder.empty()

            if response_text_juicer:
                st.download_button(
                    label="Download Summary",
                    data=response_text_juicer.encode("utf-8"),
                    file_name="summary.txt",
                    mime="text/plain"
                )
            else:
                st.write("No summary generated. Please try again.")

            st.session_state["response_text_juicer"] = response_text_juicer

            with output_container:
                output_container.empty()  # Clear the container before rendering the new response
                st.write(response_text_juicer)

        else:
            with output_container:
                output_container.empty()  # Clear the container before rendering the existing response
                if st.session_state["response_text_juicer"]:
                    st.write(st.session_state["response_text_juicer"])

    if __name__ == "__main__":
        main()


elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')