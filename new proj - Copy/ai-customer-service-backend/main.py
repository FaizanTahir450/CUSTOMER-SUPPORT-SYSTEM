import os
from dotenv import load_dotenv
from pdf_processor import PDFProcessor
from vector_store_manager import VectorStoreManager
from memory_manager import MemoryManager
from chatbot import LAMAChatbot

# LangChain agent tools
from langchain.agents import AgentExecutor, create_openai_functions_agent  # simplified agent setup

def setup_knowledge_base(pdf_path="Lama.pdf"):
    """Setup the knowledge base by processing PDF and creating vector store"""
    print("📚 Setting up knowledge base...")
    
    processor = PDFProcessor()
    chunks = processor.process_pdf(pdf_path)
    
    if not chunks:
        print("❌ Failed to process PDF. Check Lama.pdf exists.")
        return None
    
    vector_manager = VectorStoreManager()
    vector_manager.clear_vector_store()
    vector_store = vector_manager.create_vector_store(chunks)
    
    return vector_store

def main():
    load_dotenv()
    print("🤖 Initializing LAMA Customer Support AI...")
    
    PDF_PATH = "Lama.pdf"
    
    if not os.path.exists(PDF_PATH):
        print(f"❌ PDF '{PDF_PATH}' not found in current directory.")
        return
    
    vector_manager = VectorStoreManager()
    if not vector_manager.vector_store_exists():
        print("📚 First-time setup: Creating vector store from PDF...")
        vector_store = setup_knowledge_base(PDF_PATH)
        if vector_store is None:
            return
    else:
        print("📚 Loading existing knowledge base...")
        vector_store = vector_manager.load_vector_store()
    
    memory_manager = MemoryManager()
    chatbot = LAMAChatbot(vector_store, memory_manager)
    
    # Create agent manually with prompt
    agent = create_openai_functions_agent(chatbot.llm, [chatbot.retriever_tool], prompt=chatbot.prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=[chatbot.retriever_tool],
        memory=memory_manager.get_memory(),
        verbose=True
    )
    chatbot.set_agent_executor(executor)  # manually assign executor
    
    print("\n" + "=" * 60)
    print("🤖 LAMA Customer Support AI Activated!")
    print("💎 Specialized in: Company Details, Orders, Payments, Policies")
    print("📝 Type 'quit' or 'exit' to end the conversation")
    print("=" * 60)
    
    # Chat loop
    while True:
        try:
            question = input("\n💬 Customer: ").strip()
            if question.lower() in ['quit', 'exit', 'bye']:
                print("👋 Thank you for contacting LAMA Support!")
                break
            if not question:
                continue
            
            print("🔍 Searching knowledge base...")
            response = chatbot.ask(question)
            print(f"🤖 LAMA Support: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Thank you for contacting LAMA Support!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
