import streamlit as st

st.title("AI Career Agent")
st.write("This app helps students with resume and career guidance!")

name = st.text_input("Enter your name:")
query = st.text_area("Enter your question or career query:")

if st.button("Submit"):
    st.write(f"Hello {name}, I will help you with: {query}")
