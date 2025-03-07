import streamlit as st
import requests
import os

st.set_page_config(page_title="Smart Contract Manager", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Compile", "Deploy", "Interact"])

# Get the backend URL from the environment variable
backend_url = os.getenv("BACKEND_URL", "http://localhost:8040")

if page == "Compile":
    st.header("Compile Smart Contract")
    if st.button("Compile"):
        response = requests.get(f"{backend_url}/compile")
        st.write(response.json())

elif page == "Deploy":
    st.header("Deploy Smart Contract")
    if st.button("Deploy"):
        response = requests.post(f"{backend_url}/deploy")
        st.write(response.json())

elif page == "Interact":
    st.header("Interact with Smart Contract")
    contract_address = st.text_input("Enter Contract Address")
    if st.button("Call Function"):
        response = requests.post(f"{backend_url}/interact", json={"address": contract_address})
        st.write(response.json())
