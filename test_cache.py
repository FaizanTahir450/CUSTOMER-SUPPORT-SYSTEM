from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
import os, json, hashlib

CACHE_PATH = "semantic_faiss_cache"
QA_MAP_FILE = "qa_map.json"

# Load embeddings
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

# Load QA map
with open(QA_MAP_FILE, "r", encoding="utf-8") as f:
    qa_map = json.load(f)

# Deduplicate based on normalized questions
new_qa_map = {}
for index, data in qa_map.items():
    question = data["question"].strip().lower()
    new_index = hashlib.md5(question.encode()).hexdigest()

    if new_index not in new_qa_map:
        new_qa_map[new_index] = {
            "question": question,
            "answer": data["answer"],
            "count": data.get("count", 1)
        }
    else:
        # Keep higher count if duplicate found
        new_qa_map[new_index]["count"] = max(
            new_qa_map[new_index]["count"],
            data.get("count", 1)
        )

# Save cleaned QA map
with open(QA_MAP_FILE, "w", encoding="utf-8") as f:
    json.dump(new_qa_map, f, indent=2, ensure_ascii=False)

# Rebuilding FAISS cache
if os.path.exists(CACHE_PATH):
    import shutil
    shutil.rmtree(CACHE_PATH)

semantic_cache = FAISS.from_documents(
    [Document(page_content=d["question"], metadata={"index": i})
     for i, d in new_qa_map.items() if d["count"] >= 2],
    embeddings
)

# Save new FAISS index
semantic_cache.save_local(CACHE_PATH)

print(f"✅ Deduplicated and rebuilt FAISS index with {len(semantic_cache.index_to_docstore_id)} entries.")
