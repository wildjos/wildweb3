import pandas as pd
import streamlit as st
from datetime import datetime

# Helper function to shorten addresses and hashes
def shorten(value, length=15):
    return value[:8] + "..." + value[-7:] if len(value) > length else value


def make_clickable_link(base_url, path, value):
    """Helper to generate clickable links."""
    return f"[{shorten(value)}]({base_url}/{path}/{value})" if base_url and value else shorten(value)


def make_contract_address_clickable(data):
    """Creates a clickable link for contract addresses, supporting both dict and DataFrame row inputs."""
    network = data["Network"].lower() if isinstance(data, pd.Series) else data.get("network", "").lower()
    contract_address = data["Contract Address"] if isinstance(data, pd.Series) else data.get("contract_address", "")
    explorer_url = data["Explorer URL"] if isinstance(data, pd.Series) else data.get("explorer_url", "")

    if not contract_address or not explorer_url:
        return contract_address  # Return as-is if missing data

    if network == "wildjos_vtn":
        return f"[{shorten(contract_address)}]({explorer_url})"
    return f"[{shorten(contract_address)}]({explorer_url}/address/{contract_address})"


def make_deployer_address_clickable(data):
    """Creates a clickable link for deployer addresses, supporting both dict and DataFrame row inputs."""
    network = data["Network"].lower() if isinstance(data, pd.Series) else data.get("network", "").lower()
    deployer_address = data["Deployer Address"] if isinstance(data, pd.Series) else data.get("deployer_address", "")
    explorer_url = data["Explorer URL"] if isinstance(data, pd.Series) else data.get("explorer_url", "")

    if not deployer_address or not explorer_url:
        return deployer_address

    if network == "wildjos_vtn":
        return f"[{shorten(deployer_address)}]({explorer_url})"
    return f"[{shorten(deployer_address)}]({explorer_url}/address/{deployer_address})"


def make_tx_hash_clickable(data):
    """Creates a clickable link for transaction hashes, supporting both dict and DataFrame row inputs."""
    network = data["Network"].lower() if isinstance(data, pd.Series) else data.get("network", "").lower()
    tx_hash = data["Tx Hash"] if isinstance(data, pd.Series) else data.get("deployment_tx_hash", "")
    explorer_url = data["Explorer URL"] if isinstance(data, pd.Series) else data.get("explorer_url", "")

    if not tx_hash or not explorer_url:
        return tx_hash

    if not tx_hash.startswith("0x"):
        tx_hash = f"0x{tx_hash}"

    return f"[{shorten(tx_hash)}]({explorer_url}/tx/{tx_hash})"


def format_timestamp(row):
    """Formats deployment timestamp safely."""
    deployment_timestamp = row.get("Deployed At", "")

    if not deployment_timestamp:
        return "Unknown"  # Return a placeholder if missing

    try:
        return datetime.fromisoformat(deployment_timestamp).strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return "Invalid Date"  # Handle incorrect formats gracefully


def filter_contracts(contracts):
    """Applies user-selected filters for network, deployer, and contract name."""
    network_list = list(set(c["network"] for c in contracts))
    selected_network = st.selectbox("Filter by Network:", ["All"] + network_list)

    if selected_network != "All":
        contracts = [c for c in contracts if c["network"] == selected_network]

    # Filter by contract name
    contract_name_list = list(set(c["contract_name"] for c in contracts))
    selected_contract_name = st.selectbox("Filter by Contract Name:", ["All"] + contract_name_list)
    if selected_contract_name != "All":
        contracts = [c for c in contracts if c["contract_name"] == selected_contract_name]

    # Filter by deployer
    deployer_list = list(set(c["deployer_name"] for c in contracts))
    selected_deployer = st.selectbox("Filter by Deployer:", ["All"] + deployer_list)
    if selected_deployer != "All":
        contracts = [c for c in contracts if c["deployer_name"] == selected_deployer]

    # Search query for deployer address
    search_query = st.text_input("Search by Deployer Address:")
    if search_query:
        contracts = [c for c in contracts if search_query.lower() in c["deployer_address"].lower()]

    return contracts

def display_contract(contract):
    """Displays contract information in a collapsible Streamlit expander."""
    deployed_at = datetime.fromisoformat(contract["deployment_timestamp"]).strftime("%Y-%m-%d %H:%M:%S")

    with st.expander(f"Contract Name: {contract['contract_name']}"):
        st.write(f"**Network:** {contract['network']}")
        st.write(f"**Address:** {make_contract_address_clickable(contract)}")
        st.write(f"**Deployer:** {contract['deployer_name']} - {make_deployer_address_clickable(contract)}")
        st.write(f"**Tx Hash:** {make_tx_hash_clickable(contract)}")
        st.write(f"**Deployed At:** {deployed_at}")

        if st.button(f"Interact with {contract['contract_name']}", key=contract["contract_address"]):
            st.session_state["selected_contract"] = contract
            st.switch_page("pages/inbox_interaction.py")


def process_dataframe(contracts):
    """Converts contract data into a formatted DataFrame with clickable links."""
    df = pd.DataFrame(contracts)
    
    df.rename(columns={
        "id": "ID",
        "contract_name": "Contract Name",
        "contract_address": "Contract Address",
        "deployer_name": "Deployer",
        "deployer_address": "Deployer Address",
        "network": "Network",
        "deployment_tx_hash": "Tx Hash",
        "deployment_timestamp": "Deployed At",
        "explorer_url": "Explorer URL"
    }, inplace=True)

    if not df.empty:
        df["Contract Address"] = df.apply(make_contract_address_clickable, axis=1)
        df["Deployer Address"] = df.apply(make_deployer_address_clickable, axis=1)
        df["Tx Hash"] = df.apply(make_tx_hash_clickable, axis=1)
        df["Deployed At"] = df.apply(format_timestamp, axis=1)
        
        # Drop 'Explorer URL' column after use
        df.drop(columns=["Explorer URL"], inplace=True, errors="ignore")

    return df
