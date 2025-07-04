
import streamlit as st
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retreiver
from security import validate_and_sanitize 

model = OllamaLLM(model="llama3.2")

template = """
You are a Thai cuisine expert.

Below are excerpts from Thai recipes:

{reviews}

Now, based on the question below, only use **relevant information** to answer:

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

st.set_page_config(page_title="Thai Recipe Chatbot", layout="centered")
st.title("🍛 Thai Recipe Chatbot")
st.write("Ask anything about Thai cooking using real recipe data!")

with st.sidebar:
    st.header("📘 Help")
    st.info("Ask a question about Thai cuisine.\n\nYou can type your own or choose an example below!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

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

user_input = st.chat_input("Ask a Thai cooking question...", key="chat_input")

if not user_input and st.session_state.example_input:
    user_input = st.session_state.example_input
    st.session_state.example_input = ""

if user_input:
    try:
        cleaned_input = validate_and_sanitize(user_input)

     
        st.chat_message("user").markdown(cleaned_input)
        st.session_state.messages.append({"role": "user", "content": cleaned_input})

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reviews = retreiver.invoke(cleaned_input)
                answer = chain.invoke({"reviews": reviews, "question": cleaned_input})
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

    except ValueError as ve:
        st.error(f"❌ Validation Error: {ve}")
