import streamlit as st
from openai import OpenAI

# Set up the OpenAI client
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

# Custom CSS for styling
st.markdown(
    """
    <style>
    .stChatInput {
        position: fixed;
        bottom: 0;
        width: 100%;
        background-color: #f9f9f9;
        padding: 10px;
        box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 10px 15px;
        margin: 5px 0;
    }
    .stChatMessage.user {
        background-color: #0078d4;
        color: white;
        margin-left: auto;
        max-width: 70%;
    }
    .stChatMessage.assistant {
        background-color: #f1f1f1;
        color: black;
        margin-right: auto;
        max-width: 70%;
    }
    .stTitle {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0078d4;
    }
    .stHeader {
        font-size: 1.5rem;
        color: #333;
    }
    .dark-mode .stChatMessage.user {
        background-color: #1e3a8a;
        color: white;
    }
    .dark-mode .stChatMessage.assistant {
        background-color: #333;
        color: white;
    }
    .dark-mode body {
        background-color: #121212;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Streamlit app
st.markdown('<p class="stTitle">Chat with T.P.I.SAI 🤖</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="stHeader"></p>',
    unsafe_allow_html=True,
)

# Initialize session state for chat history and settings
if "messages" not in st.session_state:
    st.session_state.messages = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    temperature = st.slider("Temperature", 0.1, 1.0, 0.7)
    max_tokens = st.slider("Max Tokens", 100, 2048, 1024)
    st.session_state.dark_mode = st.checkbox("Dark Mode", value=st.session_state.dark_mode)

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.experimental_rerun()

# Apply dark mode if enabled
if st.session_state.dark_mode:
    st.markdown(
        """
        <style>
        body {
            background-color: #121212;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Display chat history
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    with st.chat_message(role):
        st.write(content)

        # Add emoji reactions for AI messages
        if role == "assistant":
            st.write("React to this message:")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👍", key=f"like_{len(st.session_state.messages)}"):
                    st.write("You liked this message!")
            with col2:
                if st.button("👎", key=f"dislike_{len(st.session_state.messages)}"):
                    st.write("You disliked this message!")

# User input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Call the NVIDIA API
                completion = client.chat.completions.create(
                    model="nvidia/llama-3.1-nemotron-70b-instruct",
                    messages=st.session_state.messages,
                    temperature=temperature,
                    top_p=1,
                    max_tokens=max_tokens,
                    stream=True,
                )

                response = ""
                response_placeholder = st.empty()
                for chunk in completion:
                    if chunk.choices[0].delta.content is not None:
                        response += chunk.choices[0].delta.content
                        response_placeholder.write(response)

                # Add AI response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"An error occurred: {e}")