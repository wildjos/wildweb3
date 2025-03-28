import streamlit as st
import requests
import os
import pandas as pd
from datetime import datetime
from utils import process_dataframe, filter_contracts, display_contract


st.set_page_config(page_title="Smart Contract Manager", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Compile", "Deploy", "Interact"])
# st.sidebar.page_link("pages/inbox_interaction.py", label="Inbox Contract Interaction")

# Get the backend URL from the environment variable
backend_url = os.getenv("BACKEND_URL", "http://localhost:8040")

if page == "Compile":
    st.header("Compile Smart Contract")

    # upload a file:
    uploaded_file = st.file_uploader("Upload a Solidity file", type=["sol"])

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

    response = requests.get(f"{backend_url}/networks")
    if response.status_code == 200:
        networks = response.json().get("networks")
        selected_network = st.selectbox("Select network to deploy to", networks)

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
                    response = requests.post(f"{backend_url}/deploy", json={"network_name": selected_network, "contract_name": selected_contract, "user": user, "constructor_args": constructor_args})
                    st.write(response.json())

                    if response.status_code == 200:
                        st.success("Deployment Successful!")
                        st.json(response.json())
                    else:
                        st.error(f"Deployment failed: {response.text}")
        else:
            st.error("Failed to fetch compiled contracts.")
    else:
        st.error("Failed to get available networks")



elif page == "Interact":
    st.header("Interact with Smart Contract")


    response = requests.get(f"{backend_url}/metadata/contracts")
    if response.status_code == 200:
        
        contracts = response.json().get("contracts", [])

        # Tabs for viewing full data and filtering
        full_tab, filter_tab = st.tabs(["Full Table", "Filter"])

        # FULL TABLE: Show all contracts
        with full_tab:
            df = process_dataframe(contracts)
            st.markdown(df.to_markdown(index=False), unsafe_allow_html=True)

        # FILTER TAB: Allow filtering
        with filter_tab:
            filtered_contracts = filter_contracts(contracts)

            st.write(f"**Filtered Results: {len(filtered_contracts)} contracts found**")
            for contract in filtered_contracts:
                display_contract(contract)  
  
    else:
        error_message = response.json().get("detail", "Failed to fetch deployed contracts")
        st.error(f"Error: {error_message}")
