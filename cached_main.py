from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retreiver
from caching import search_similar_question, add_to_semantic_cache

# RAG Chain setup 
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
    question = input("Ask your question (q to quit): ").strip()
    print("\n\n")

    if question.lower() == 'q':
        break

    cached_answer = search_similar_question(question)
    if cached_answer:
        print("🔁 Retrieved from memory (semantic match):")
        print(cached_answer)
        continue

    reviews = retreiver.invoke(question)
    result = chain.invoke({"reviews": reviews, "question": question})
    final_answer = result.content if hasattr(result, "content") else str(result)

    print(final_answer)
    add_to_semantic_cache(question, final_answer)
