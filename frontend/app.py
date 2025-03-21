import streamlit as st
import requests
import os
import pandas as pd
from datetime import datetime

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


    # I want to get all the contracts that have been deployed and display in a table
    response = requests.get(f"{backend_url}/metadata/contracts")
    print("got a respnse")
    print(response)
    if response.status_code == 200:
        
        contracts = response.json().get("contracts", [])

        print(f"DEPLOYED CONTRACTS: {contracts}")

        # Convert list of dictionaries to a DataFrame for better display
        df = pd.DataFrame(contracts)

        # Helper function to shorten addresses and hashes
        def shorten(text):
            return f"{text[:8]}.....{text[-7:]}"

        # Rename columns for better display
        df.rename(columns={
            "id": "ID",
            "contract_name": "Contract Name",
            "contract_address": "Contract Address",
            "deployer_name": "Deployer",
            "deployer_address": "Deployer Address",
            "network": "Network",
            "deployment_tx_hash": "Tx Hash",
            "deployment_timestamp": "Deployed At",
        }, inplace=True)


        # Make the contract addresses, deployer addresses, and transaction hashes clickable
        df["Contract Address"] = df["Contract Address"].apply(lambda x: f"[{shorten(x)}](https://sepolia.etherscan.io/address/{x})")
        df["Deployer Address"] = df["Deployer Address"].apply(lambda x: f"[{shorten(x)}](https://sepolia.etherscan.io/address/{x})")
        df["Tx Hash"] = df["Tx Hash"].apply(lambda x: f"[{shorten(x)}](https://sepolia.etherscan.io/tx/{x})")

        smart_contract_list = list(set(contract["contract_name"] for contract in contracts))
        selected_smart_contract = st.selectbox("Filter by Smart Contract:", ["All"] + smart_contract_list)

        if selected_smart_contract != "All":
            contracts = [c for c in contracts if c["contract_name"] == selected_smart_contract]

        st.markdown(df.to_markdown(index=False), unsafe_allow_html=True)

        search_query = st.text_input("Search by Deployer Name or Address:")
        if search_query:
            contracts = [c for c in contracts if search_query.lower() in c["deployer_name"].lower() or search_query.lower() in c["deployer_address"].lower()]


        for contract in contracts:
            deployed_at = datetime.fromisoformat(contract["deployment_timestamp"]).strftime("%Y-%m-%d %H:%M:%S")

            with st.expander(f"{contract['contract_name']} ({contract['network']})"):
                st.write(f"**Address:** [{contract['contract_address']}](https://sepolia.etherscan.io/address/{contract['contract_address']})")
                st.write(f"**Deployer:** {contract['deployer_name']} - [{contract['deployer_address']}](https://sepolia.etherscan.io/address/{contract['deployer_address']})")
                st.write(f"**Tx Hash:** [{contract['deployment_tx_hash']}](https://sepolia.etherscan.io/tx/{contract['deployment_tx_hash']})")
                st.write(f"**Deployed At:** {deployed_at}")

                if st.button(f"Interact with {contract['contract_name']}", key=contract["contract_address"]):
                    st.session_state["selected_contract"] = contract  # Store contract details
                    st.switch_page("pages/inbox_interaction.py")  # Correct format (no "pages/" and no ".py"))


    else:
        error_message = response.json().get("detail", "Failed to fetch deployed contracts")
        st.error(f"Error: {error_message}")

