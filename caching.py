from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
import hashlib
import os
import json
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore  # ✅ updated import

CACHE_PATH = "semantic_faiss_cache"
QA_MAP_FILE = "qa_map.json"

embeddings = OllamaEmbeddings(model="mxbai-embed-large")

semantic_cache = None
qa_map = {}

# Load existing cache if available
if os.path.exists(CACHE_PATH):
    semantic_cache = FAISS.load_local(CACHE_PATH, embeddings, allow_dangerous_deserialization=True)
    with open(QA_MAP_FILE, "r", encoding="utf-8") as f:
        qa_map = json.load(f)

    print("\n--- FAISS Stored Questions ---")
    for i, doc in enumerate(semantic_cache.docstore._dict.values()):
        print(f"{i+1}. {doc.page_content}")
    print(f"--- Total vectors in FAISS: {semantic_cache.index.ntotal}\n")


def has_shared_keywords(q1, q2, min_overlap=1):
    """Check if two questions share at least N important words."""
    stopwords = {"how", "do", "i", "the", "a", "an", "to", "make", "for", "of", "is", "in", "recipe"}
    words1 = set(q1.lower().split()) - stopwords
    words2 = set(q2.lower().split()) - stopwords
    return len(words1 & words2) >= min_overlap


def search_similar_question(query, k=1, score_threshold=0.5):
    """
    Search for a semantically similar question.
    For L2 distance: lower scores mean closer matches.
    Still checks for minimal keyword overlap to avoid irrelevant matches.
    """
    if semantic_cache is None:
        return None

    results = semantic_cache.similarity_search_with_score(query, k=k)
    if not results:
        return None

    doc, score = results[0]
    print(f"FAISS match distance: {score:.4f} — Q: {doc.page_content}")

    # For L2 distance: closer = smaller distance
    if score <= score_threshold and has_shared_keywords(query, doc.page_content):
        index = doc.metadata.get("index")
        if index and index in qa_map and "answer" in qa_map[index]:
            qa_map[index]["count"] += 1
            with open(QA_MAP_FILE, "w", encoding="utf-8") as f:
                json.dump(qa_map, f, indent=2, ensure_ascii=False)
            print("✅ Found semantic match — returning cached answer")
            return qa_map[index]["answer"]

    print("❌ No close enough match — generating fresh answer.")
    return None


def add_to_semantic_cache(question, answer):
    global semantic_cache

    if semantic_cache is None:
        # Create an empty FAISS index with the correct dimension
        dim = len(embeddings.embed_query("test"))
        index = faiss.IndexFlatL2(dim)
        semantic_cache = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=InMemoryDocstore(),  # ✅ updated to correct import
            index_to_docstore_id={}
        )

    index = hashlib.md5(question.encode()).hexdigest()

    if index not in qa_map:
        qa_map[index] = {
            "question": question,
            "answer": answer,
            "count": 1
        }

        doc = Document(page_content=question, metadata={"index": index})
        semantic_cache.add_documents([doc])

        semantic_cache.save_local(CACHE_PATH)
        with open(QA_MAP_FILE, "w", encoding="utf-8") as f:
            json.dump(qa_map, f, indent=2, ensure_ascii=False)

        print(f"✅ Added new Q&A to cache: {question}")
    else:
        qa_map[index]["count"] += 1
        with open(QA_MAP_FILE, "w", encoding="utf-8") as f:
            json.dump(qa_map, f, indent=2, ensure_ascii=False)


def test_similarity(query):
    if semantic_cache:
        print(f"\n🔍 Testing similarity for: {query}")
        results = semantic_cache.similarity_search_with_score(query, k=3)
        for doc, score in results:
            print(f"Score: {score:.4f} — Q: {doc.page_content}")
