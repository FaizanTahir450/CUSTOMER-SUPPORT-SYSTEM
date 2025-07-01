from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retreiver

model = OllamaLLM(model="lifelongeek/raft_llama3.2_1b-Q4_K_M")

template = """
You are a Thai cuisine expert.

Below are excerpts from Thai recipes:

{reviews}

Now, based on the question below, only use **relevant information** to answer:

Question: {question}
"""


prompt = ChatPromptTemplate.from_template(template)
#Prompt is being passed to the model 
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