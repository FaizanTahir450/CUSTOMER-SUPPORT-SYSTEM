from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retreiver

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

while True:
    print("\n\n------------------------------------------")
    question = input("Ask your question (q to quit): ")
    print("\n\n")

    if question=='q':
        break

    reviews = retreiver.invoke(question)
    result = chain.invoke({"reviews": reviews, "question": question})
    print(result)