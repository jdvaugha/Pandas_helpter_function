import streamlit as st
import json
from openai import OpenAI

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = ''
if 'client' not in st.session_state:
    st.session_state.client = None
if 'models' not in st.session_state:
    st.session_state.models = ["chatgpt-4o-latest", "gpt-4-turbo"]
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = "chatgpt-4o-latest"
if 'custom_prompt' not in st.session_state:
    st.session_state.custom_prompt = "You are a helpful assistant."
if 'temperature' not in st.session_state:
    st.session_state.temperature = 0.5  # Default temperature value

st.title("Pandas Helper")

# Sidebar settings
with st.sidebar:
    st.header("Settings")

    # API key input
    api_key = st.text_input("API key:", type="password")
    if api_key and api_key != st.session_state.openai_api_key:
        st.session_state.openai_api_key = api_key
        st.session_state.client = OpenAI(api_key=api_key)

    # Model selection
    st.session_state.selected_model = st.selectbox(
        "Select model:", st.session_state.models
    )

    # Custom prompt input
    st.session_state.custom_prompt = st.text_area(
        "Custom System Prompt:",
        value=st.session_state.custom_prompt,
        height=100,
    )

    # Temperature slider
    st.session_state.temperature = st.slider(
        "Adjust Temperature:",
        min_value=0.0, max_value=1.0, value=st.session_state.temperature, step=0.1
    )

    # Clear chat history button
    if st.button("Clear Chat History", key="clear_button"):
        st.session_state.messages = []
        st.rerun()

# Chat interface
if st.session_state.client:
    st.subheader("Chat with Pandas Helper")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    user_input = st.text_input("Type your message here:", key=f"user_input_{len(st.session_state.messages)}")

    # Send button
    if st.button("Send", key="send_button"):
        if user_input:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # Prepare system prompt and user messages
            full_messages = [{"role": "system", "content": st.session_state.custom_prompt}]
            full_messages.extend(st.session_state.messages)

            # Generate AI response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""

                # Make the API call
                response = st.session_state.client.chat.completions.create(
                    model=st.session_state.selected_model,  # Use the selected model
                    messages=full_messages,
                    temperature=st.session_state.temperature,
                )

                # Convert the response to a dictionary
                response_dict = json.loads(response.model_dump_json())

                # Access the content from the response dictionary
                full_response = response_dict['choices'][0]['message']['content']
                message_placeholder.markdown(full_response)

            # Add AI response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})

            # Rerun to update UI
            st.rerun()

else:
    st.warning("Please enter your OpenAI API key to start chatting.")
