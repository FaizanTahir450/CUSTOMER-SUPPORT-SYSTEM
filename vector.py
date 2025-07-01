from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_community.document_loaders import PyMuPDFLoader
import os
import shutil

# === Configuration ===
pdf_path = "ThaiRecipes.pdf"
db_location = "./chroma_langchain_db"
collection_name = "thai_recipes"

# === Optional: Reset DB if needed (force re-embed)
if os.path.exists(db_location):
    shutil.rmtree(db_location)

# === Load PDF Pages ===
loader = PyMuPDFLoader(pdf_path)
pages = loader.load()

# === Embedding model ===
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

# === Initialize vector store ===
vector_store = Chroma(
    collection_name=collection_name,
    persist_directory=db_location,
    embedding_function=embeddings
)

# === Add PDF pages to the vector store ===
documents = []
ids = []

for i, page in enumerate(pages):
    document = Document(
        page_content=page.page_content,
        metadata={"source": f"page_{i+1}"},
        id=str(i)
    )
    documents.append(document)
    ids.append(str(i))

vector_store.add_documents(documents=documents, ids=ids)

# === Create retriever ===
# k: "Decides the no- of top (similar) results we want to display"
retreiver = vector_store.as_retriever(search_kwargs={"k": 10})
