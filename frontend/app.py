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

    # upload a file:
    uploaded_file = st.file_uploader("Upload a Solidty file", type=["sol"])

    if uploaded_file is not None:
        st.write(f"File {uploaded_file.name} uploaded successfully.")

        if st.button("Compile"):

            # Spinner to feedback to user
            with st.spinner("Compiling....", show_time=True):

                files = {"file": (uploaded_file.name, uploaded_file, "text/plain")}
                response = requests.post(f"{backend_url}/compile", files=files)
                st.write(response.json())

                if response.status_code == 200:
                    st.success("Compilation Successful!")
                    # Display JSON output
                    st.json(response.json())  
                else:
                    st.error(f"Compilation failed: {response.text}")


elif page == "Deploy":
    st.header("Deploy Smart Contract")

    # Get the list of compiled contracts
    response = requests.get(f"{backend_url}/compiled_contracts")
    if response.status_code == 200:
        compiled_contracts = response.json()
        contract_names = [contract['name'] for contract in compiled_contracts]
        selected_contract = st.selectbox("Select Contract to Deploy", contract_names)

        # Need to handle contracts with constructor arguments
        constructor_args = st.text_input("Constructor Arguments (comma-separated)").split(',')

        user = st.selectbox("Select User", ['alice', 'bob', 'charlie'])

        if st.button("Deploy"):
            with st.spinner("Deploying..."):
                response = requests.post(f"{backend_url}/deploy", json={"contract_name": selected_contract, "user": user, "constructor_args": constructor_args})
                st.write(response.json())

                if response.status_code == 200:
                    st.success("Deployment Successful!")
                    st.json(response.json())
                else:
                    st.error(f"Deployment failed: {response.text}")
    else:
        st.error("Failed to fetch compiled contracts.")



elif page == "Interact":
    st.header("Interact with Smart Contract")
    contract_address = st.text_input("Enter Contract Address")
    if st.button("Call Function"):
        response = requests.post(f"{backend_url}/interact", json={"address": contract_address})
        st.write(response.json())
