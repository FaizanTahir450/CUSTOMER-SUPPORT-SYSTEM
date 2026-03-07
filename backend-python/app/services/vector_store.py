# vector_store.py
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from app.config import Config
import os
import pypdf

_vector_store = None
CHROMA_PERSIST_DIRECTORY = "chroma_db"

def load_pdf_documents(pdf_path: str):
    """Load PDF using pypdf directly"""
    documents = []
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                if text.strip():  # Only add pages with content
                    documents.append(
                        Document(
                            page_content=text,
                            metadata={"source": pdf_path, "page": page_num}
                        )
                    )
    except Exception as e:
        print(f"❌ Error loading PDF: {e}")
    
    return documents

def init_vector_store():
    global _vector_store
    
    if _vector_store is not None:
        return
    
    # Create embeddings using OpenRouter
    embeddings = OpenAIEmbeddings(
        openai_api_key=Config.OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1"
    )
    
    # Check if Chroma database already exists
    if os.path.exists(CHROMA_PERSIST_DIRECTORY) and os.listdir(CHROMA_PERSIST_DIRECTORY):
        print(f"📦 Loading existing Chroma vector store from {CHROMA_PERSIST_DIRECTORY}")
        try:
            _vector_store = Chroma(
                persist_directory=CHROMA_PERSIST_DIRECTORY,
                embedding_function=embeddings
            )
            # Check if it has any documents
            collection_count = _vector_store._collection.count()
            print(f"✅ Chroma vector store loaded with {collection_count} documents")
            return
        except Exception as e:
            print(f"⚠️ Error loading Chroma store: {e}")
            print("Creating new vector store...")
    
    # Create new vector store if it doesn't exist or is empty
    print("🔄 Creating new Chroma vector store...")
    pdf_path = Config.PDF_PATH
    
    # Check if PDF exists
    if not os.path.exists(pdf_path):
        print(f"⚠️ Warning: PDF file {pdf_path} not found. Creating vector store with sample data.")
        documents = []
    else:
        # Load PDF using pypdf directly
        documents = load_pdf_documents(pdf_path)
        print(f"📄 Loaded {len(documents)} pages from {pdf_path}")
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    if documents:
        split_docs = text_splitter.split_documents(documents)
        print(f"✂️ Split into {len(split_docs)} chunks")
    else:
        # Fallback sample documents if PDF not found
        split_docs = [
            Document(
                page_content="Our company offers 24/7 customer support via chat, email, and phone.",
                metadata={"source": "default"}
            ),
            Document(
                page_content="We provide free shipping on orders over $50 and have a 30-day return policy.",
                metadata={"source": "default"}
            )
        ]
        print("⚠️ Using sample documents")
    
    # Create Chroma vector store with persistence
    _vector_store = Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings,
        persist_directory=CHROMA_PERSIST_DIRECTORY
    )
    
    print(f"✅ Chroma vector store created and persisted to {CHROMA_PERSIST_DIRECTORY}")
    print(f"📊 Total documents in store: {_vector_store._collection.count()}")

def get_vector_store():
    global _vector_store
    
    if _vector_store is None:
        init_vector_store()
    
    return _vector_store

def search_company_info(query: str, k: int = 3):
    """Search the vector store for relevant company information"""
    vector_store = get_vector_store()
    
    try:
        docs = vector_store.similarity_search(query, k=k)
        return docs
    except Exception as e:
        print(f"❌ Error searching vector store: {e}")
        return []

def add_documents(documents: list[Document]):
    """Add new documents to the existing vector store"""
    vector_store = get_vector_store()
    
    try:
        vector_store.add_documents(documents)
        print(f"✅ Added {len(documents)} documents to vector store")
    except Exception as e:
        print(f"❌ Error adding documents: {e}")

def delete_collection():
    """Delete the entire Chroma collection (useful for reset)"""
    global _vector_store
    
    try:
        if _vector_store is not None:
            _vector_store.delete_collection()
            _vector_store = None
        
        # Also remove the directory
        import shutil
        if os.path.exists(CHROMA_PERSIST_DIRECTORY):
            shutil.rmtree(CHROMA_PERSIST_DIRECTORY)
        
        print("✅ Vector store collection deleted")
    except Exception as e:
        print(f"❌ Error deleting collection: {e}")