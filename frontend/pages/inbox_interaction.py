import os
import requests
import streamlit as st
from utils import make_tx_hash_clickable

# Get the backend URL from the environment variable
backend_url = os.getenv("BACKEND_URL", "http://localhost:8040")
st.title("Inbox Smart Contract Interaction")


# Initialise session states
if 'selected_contract' not in st.session_state:
    st.session_state.selected_contract = None


# Initialize variables
message = "N/A"
counter = 0

import streamlit as st


# -------------------------------------------------------------------------------
# Source Information
if st.session_state.selected_contract is not None:

    network = st.session_state.selected_contract.get('network')
    contract_address = st.session_state.selected_contract.get("contract_address")
    contract_name = st.session_state.selected_contract.get('contract_name')
    deployer_name = st.session_state.selected_contract.get("deployer_name")

    # Fetch stored message
    response = requests.get(f"{backend_url}/inbox/message", \
                            params={"network": network, \
                                    "contract_address": contract_address, \
                                    "contract_name": contract_name})

    if response.status_code == 200:
        message = response.json().get("message", "N/A")
    else:
        st.error(f"Get message failed: {response.text}")

    # Fetch counter value
    response = requests.get(f"{backend_url}/inbox/counter", \
                            params={"network": network, \
                                    "contract_address": contract_address, \
                                    "contract_name": contract_name})

    if response.status_code == 200:
        counter = response.json().get("count", 0)
    else:
        st.error(f"Get counter failed: {response.text}")


    # -------------------------------------------------------------------------------
    # User Information part: Create two columns for better layout
    st.subheader("Contract Information")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"***Contract Address***:")
        st.code(contract_address, language="plaintext")
        st.write(f"***Network***: {network}")
        st.write(f"***Contract Name***: {contract_name}")

    with col2:
        st.write(f"***Contract Owner***:")
        st.code(deployer_name, language="plaintext")
        st.write(f"***Current Message***: {message}")
        st.write(f"***Update Count***: {counter}")

    st.divider()


    # -------------------------------------------------------------------------------
    # Define Columns
    col_left, col_right = st.columns(2)

    # -------------------------------------------------------------------------------
    # Set New Message 
    with col_left: 
        with st.form('message'):
            st.subheader("Update message")
            new_message = st.text_input("Enter a new message:")


            # Select the user that is interacting
            response = requests.get(f"{backend_url}/users")
            if response.status_code == 200:
                users = response.json().get("users")
                user = st.selectbox("Select user account to send transaction", users)

            message_submit = st.form_submit_button('Update Message')
            if message_submit:
                if new_message:
                    response = requests.put(f"{backend_url}/inbox/update", \
                                json={"message": new_message, \
                                    "network": network, \
                                    "contract_name": contract_name, \
                                    "contract_address": contract_address, \
                                    "user_account": user})
                    
                    
                    if response.status_code == 200:
                        
                        # expect: {"success": True, "tx_hash": tx_hash}
                        tx_hash = response.json().get("tx_hash", "N/A")
                        print(f"transaction hash = {tx_hash}")
                        st.success("Message updated successfully!")

                        data = {}
                        data["network"] = network
                        data["deployment_tx_hash"] = tx_hash

                        # Fetch the explorer URL for the network
                        explorer_response = requests.get(f"{backend_url}/explorer", params={"network": network})

                        if explorer_response.status_code == 200:
                            explorer_url = explorer_response.json().get("explorer_url", None)
                            data["explorer_url"] = explorer_url
                        else:
                            st.error(f"Failed to fetch explorer URL: {explorer_response.text}")
                            data["explorer_url"] = None

                        # Display the clickable transaction hash
                        st.write(f"**View transaction on {network}:** {make_tx_hash_clickable(data)}")
                        
                    else:
                        st.error(f"Update failed: {response.text}")

    # -------------------------------------------------------------------------------
    # Math function interaction

    with col_right: 
        with st.form('maths'):
            st.subheader("Maths operations")
            a = st.number_input("Enter first number (a)", value=0, step=1)
            b = st.number_input("Enter second number (b)", value=0, step=1)

            submit = st.form_submit_button('Calculate')
            if submit:
                response = requests.post(f"{backend_url}/inbox/maths", \
                                json={"a": a, "b": b, \
                                    "network": network, \
                                    "contract_name": contract_name,
                                    "contract_address": contract_address})

                if response.status_code == 200:
                    result = response.json()
                    sum_ = result.get("sum")
                    diff = result.get("diff")
                    product = result.get("product")
                    is_zero = result.get("is_zero")
                else:
                    st.error(f"Math operation failed: {response.text}")
                    sum_, diff, product, is_zero = None, None, None, None

                # Display results
                st.write(f"Sum: {sum_}")
                st.write(f"Difference: {diff}")
                st.write(f"Product: {product}")
                st.write(f"Is A Zero? {'Yes' if is_zero else 'No'}")
else:
    st.write("No contract selected! Try selecting one from the main Navigation -> Interact -> Filter")

