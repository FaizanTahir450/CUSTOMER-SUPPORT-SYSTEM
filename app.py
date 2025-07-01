import streamlit as st
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retreiver  # Ensure this exists and works

# Load the model
model = OllamaLLM(model="llama3.2")

# Prompt template
template = """
You are a Thai cuisine expert.

Below are excerpts from Thai recipes:

{reviews}

Now, based on the question below, only use **relevant information** to answer:

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# Streamlit page setup
st.set_page_config(page_title="Thai Recipe Chatbot", layout="centered")
st.title("🍛 Thai Recipe Chatbot")
# st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/Pad_Thai_kung_Chang_Khien_street_stall.jpg/640px-Pad_Thai_kung_Chang_Khien_street_stall.jpg", use_container_width=True)
st.write("Ask anything about Thai cooking using real recipe data!")

# Sidebar help
with st.sidebar:
    st.header("📘 Help")
    st.info("Ask a question about Thai cuisine.\n\nYou can type your own or choose an example below!")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Example questions
example_qs = [
    "What are common Thai curry ingredients?",
    "How do I make Tom Yum soup?",
    "What's the difference between red and green curry?"
]

st.markdown("#### 📌 Example Questions:")
selected_example = st.selectbox("Choose one to autofill:", [""] + example_qs)
if selected_example:
    st.session_state.example_input = selected_example
else:
    st.session_state.example_input = ""

# Chat input
user_input = st.chat_input("Ask a Thai cooking question...", key="chat_input")

# Prefer example question if selected
if not user_input and st.session_state.example_input:
    user_input = st.session_state.example_input
    st.session_state.example_input = ""

if user_input:
    # Show user message
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                reviews = retreiver.invoke(user_input)
                answer = chain.invoke({"reviews": reviews, "question": user_input})
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                error_msg = f"⚠️ Error: {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

