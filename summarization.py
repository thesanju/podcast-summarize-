import streamlit as st
from openai import OpenAI
import os

client = OpenAI()
client.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(
    page_title="Summarization",
    page_icon="🖊️",
)


def Summarize_text(prompt):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "Based on the provided transcript, craft a comprehensive chapter that distils the essence of the conversation for our book targeted at entrepreneurs worldwide. This chapter, ideally 1,500 words or up to 10 minutes of reading time, should be presented in a professional tone reminiscent of a British journalist. It aims to cater to college-educated entrepreneurs seeking actionable solutions to their business challenges. Your narrative should summarise and transform the conversation into an engaging, standalone piece that outlines key insights, strategies, and personal stories the interviewee shares.Additionally, enrich the chapter by incorporating one piece of relevant industry research supporting the discussed marketing strategy or business solution. This research should be contemporary and applicable, enhancing the credibility and depth of the advice given. Ensure to include a citation link for the research in the notes, adhering to proper academic standards. The chapter should weave together practical advice, inspiration, and actionable strategies, rendered in a style consistent with The Economist, to ensure coherence and uniformity across our publication. This article aims to give the impression that the reader is conversing with the speaker. Use the following structure with 4 sections. - Prologue - Introduction: [200 words] - The Opportunity (200 - 250 words) - Crossing the chasm: [900 words] - Epilogue - Reflections: [200 words] remember this the overall article must be 1300-1500 words  make sure to Include at least one quote from the interviewee in each section that will make an impact or give tips to the readers who are young entrepreneurs. Do not mention that the interviewee is a guest on the podcast. This service is provided by UnNoticed Ventures Ltd., focusing on transforming insightful conversations into impactful written content for entrepreneurs."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=5000
    )
    return completion


def main():
    st.title("JIM's Transcription App")
    prompt = st.text_input("Enter the prompt or questions")

    uploaded_file = st.file_uploader("Upload a text file", type=["txt"])
    if uploaded_file is not None:
        uploaded_text = uploaded_file.read().decode("utf-8")
        prompt += "\n\n" + uploaded_text

    st.header("Summarization")
    
    if st.button("Generate Summary"):
        completion = Summarize_text(prompt)
        st.write(completion.choices[0].message.content)


if __name__ == "__main__":
    main()