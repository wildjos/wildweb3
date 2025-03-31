import os
import requests
import streamlit as st

# Get the backend URL from the environment variable
backend_url = os.getenv("BACKEND_URL", "http://localhost:8040")
st.title("Inbox Smart Contract Interaction")

if st.session_state.selected_contract is not None:
    st.write(f"**Contract**: {st.session_state.selected_contract}")

# Initialize variables
message = "N/A"
counter = 0

# Fetch stored message
response = requests.get(f"{backend_url}/inbox/message")
if response.status_code == 200:
    message = response.json().get("message", "N/A")
else:
    st.error(f"Get message failed: {response.text}")

# Fetch counter value
response = requests.get(f"{backend_url}/inbox/counter")
if response.status_code == 200:
    counter = response.json().get("count", 0)
else:
    st.error(f"Get counter failed: {response.text}")

# Display contract state
st.write(f"**Stored Message:** {message}")
st.write(f"**Message Update Count:** {counter}")

# Set new message
new_message = st.text_input("Enter a new message:")
if st.button("Update Message"):
    if new_message:
        response = requests.put(f"{backend_url}/inbox/update", json={"message": new_message})
        if response.status_code == 200:
            st.success("Message updated successfully!")
        else:
            st.error(f"Update failed: {response.text}")

# Math function interaction
st.subheader("Math Operations")
a = st.number_input("Enter first number (a)", value=0, step=1)
b = st.number_input("Enter second number (b)", value=0, step=1)

if st.button("Calculate"):
    response = requests.post(f"{backend_url}/inbox/maths", json={"a": a, "b": b})
    if response.status_code == 200:
        result = response.json()
        sum_ = result.get("sum")
        diff = result.get("diff")
        product = result.get("product")
        is_zero = result.get("is_zero")  # Fix casing
    else:
        st.error(f"Math operation failed: {response.text}")
        sum_, diff, product, is_zero = None, None, None, None

    # Display results
    st.write(f"Sum: {sum_}")
    st.write(f"Difference: {diff}")
    st.write(f"Product: {product}")
    st.write(f"Is A Zero? {'Yes' if is_zero else 'No'}")
