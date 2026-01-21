import streamlit as st
from openai import OpenAI
import os

# Page Config
st.set_page_config(page_title="vLLM Chat", page_icon="🤖", layout="centered")

# Custom CSS for "Premium" feel
st.markdown("""
<style>
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
    }
    .stTextInput input {
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.title("Configuration")
api_base = os.getenv("VLLM_API_BASE", "http://vllm-service:8000/v1")
api_key = os.getenv("VLLM_API_KEY", "sk-admin-token-12345")

# Initialize Client
client = OpenAI(api_key=api_key, base_url=api_base)

# Model Selection
try:
    models = client.models.list()
    model_names = [m.id for m in models.data]
    selected_model = st.sidebar.selectbox("Select Model", model_names, index=0)
except Exception as e:
    st.sidebar.error(f"Could not fetch models: {e}")
    selected_model = "casperhansen/llama-3-8b-instruct-awq"

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat
st.title("🤖 vLLM Inference Platform")
st.caption(f"Running on {selected_model}")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("What is your question?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=selected_model,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
            max_tokens=512,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
