from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
import hashlib
import os
import json

CACHE_PATH = "semantic_faiss_cache"
QA_MAP_FILE = "qa_map.json"

embeddings = OllamaEmbeddings(model="mxbai-embed-large")

semantic_cache = None
qa_map = {}

if os.path.exists(CACHE_PATH):
    semantic_cache = FAISS.load_local(CACHE_PATH, embeddings, allow_dangerous_deserialization=True)
    with open(QA_MAP_FILE, "r", encoding="utf-8") as f:
        qa_map = json.load(f)

    #Print stored documents in FAISS
    print("\n --- FAISS Stored Questions:")
    for i, doc in enumerate(semantic_cache.docstore._dict.values()):
        print(f"{i+1}. {doc.page_content}")
    print(f"\n --- Total vectors in FAISS: {semantic_cache.index.ntotal}\n")


# to search semantic cache
def search_similar_question(query, k=1, score_threshold=0.4):
    if semantic_cache is None:
        return None

    results = semantic_cache.similarity_search_with_score(query, k=k)
    if results:
        doc, score = results[0]
        print(f"--- FAISS match score: {score:.4f} — Q: {doc.page_content}")

        if score < score_threshold:
            index = doc.metadata.get("index")
            if index and index in qa_map and "answer" in qa_map[index]:
                qa_map[index]["count"] += 1

                with open(QA_MAP_FILE, "w", encoding="utf-8") as f:
                    json.dump(qa_map, f, indent=2, ensure_ascii=False)

                if qa_map[index]["count"] >= 2:
                    print("🔁 Retrieved from memory (semantic match):")
                    return qa_map[index]["answer"]
            else:
                print("⚠️ Match found but not cached yet (missing answer)")
        else:
            print("⚠️ FAISS match score too high — ignoring cached match.")

    return None


# tsaving new Q&As
def add_to_semantic_cache(question, answer):
    if semantic_cache is None:
        return

    results = semantic_cache.similarity_search_with_score(question, k=1)
    if results:
        doc, score = results[0]
        if score < 0.6:
            return  # Skip adding too-similar question

    index = hashlib.md5(question.encode()).hexdigest()

    if index in qa_map:
        qa_map[index]["count"] += 1
    else:
        qa_map[index] = {"question": question, "answer": answer, "count": 1}

    with open(QA_MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(qa_map, f, indent=2, ensure_ascii=False)

    if qa_map[index]["count"] == 2:
        doc = Document(page_content=question, metadata={"index": index})
        semantic_cache.add_documents([doc])
        semantic_cache.save_local(CACHE_PATH)  # ✅ Save updated FAISS index
        print(f"✅ Added and saved new doc: {question}")


# printing results for testing/ debugging
def test_similarity(query):
    if semantic_cache:
        print(f"\n🔍 Testing similarity for: {query}")
        results = semantic_cache.similarity_search_with_score(query, k=3)
        for doc, score in results:
            print(f"Score: {score:.4f} — Q: {doc.page_content}")
