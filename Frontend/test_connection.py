
import requests
import streamlit as st

st.title("CommerceAI — Backend Connection Test")

url = "http://127.0.0.1:5000/api/agent/ask"

st.write("Testing URL:", url)
st.write("Testing POST request to Flask...")

try:
    response = requests.post(
        url,
        json={"question": "What is our total revenue?"},
        timeout=90
    )

    st.write("HTTP status:", response.status_code)

    try:
        data = response.json()
        st.success("Flask returned a JSON response.")
        st.json(data)
    except ValueError:
        st.error("Flask did not return valid JSON.")
        st.code(response.text[:3000])

except requests.exceptions.RequestException as exc:
    st.error("Request failed.")
    st.exception(exc)
