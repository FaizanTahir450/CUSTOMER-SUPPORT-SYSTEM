from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retreiver
from caching import search_similar_question, add_to_semantic_cache

# 🔹 LangChain built-in cache (exact match)
from langchain_core.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
set_llm_cache(SQLiteCache(database_path=".llm_cache.db"))

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
    print("\n------------------------------------------")
    question = input("Ask your question (q to quit): ").strip()
    print()

    if question.lower() == 'q':
        break

    # Step 1: Check FAISS semantic cache
    cached_answer = search_similar_question(question)
    if cached_answer:
        print("🔁 Retrieved from semantic cache:")
        print(cached_answer)
        continue

    # Step 2: Retrieve from retriever and run LLM (with LangChain cache automatically applied)
    reviews = retreiver.invoke(question)
    result = chain.invoke({"reviews": reviews, "question": question})
    final_answer = result.content if hasattr(result, "content") else str(result)

    print(final_answer)

    # Step 3: Store in semantic cache for future similar queries
    add_to_semantic_cache(question, final_answer)
