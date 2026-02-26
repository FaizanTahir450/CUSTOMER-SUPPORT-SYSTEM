# graph.py
from langgraph.graph import StateGraph, END
from typing import TypedDict
from models.classifiers import classify_query, classify_relevant_query
from utils.memory import LLMCustomerSupportMemory
from services.vector_store import search_company_info
from database.db import get_order_info
from services.llm import get_llm

class SupportState(TypedDict):
    user_id: str
    message: str
    response: str
    classification: str
    sub_classification: str
    context: str
    memory: LLMCustomerSupportMemory

def classify_node(state: SupportState) -> SupportState:
    classification = classify_query(state["message"])
    state["classification"] = classification
    return state

def extract_memory_node(state: SupportState) -> SupportState:
    """Extract facts from user message and update memory"""
    memory = state["memory"]
    memory.update_memory(state["message"])
    return state

def handle_greeting(state: SupportState) -> SupportState:
    memory_context = state["memory"].get_memory_json()
    llm = get_llm()
    response = llm.invoke(
        f"You are 'Sophia', Lama retail's customer support agent. "
        f"Respond politely and briefly. "
        f"Choose ONLY ONE language (English OR Urdu), not both. "
        f"Reply in the SAME language as the user's message. "
        f"Customer context: {memory_context}\n"
        f"User message: {state['message']}"
    )
    state["response"] = response.content
    return state

def handle_irrelevant(state: SupportState) -> SupportState:
    state["response"] = "I'm a customer support assistant. I can ONLY help you with questions about our company, services, or your orders. How can I assist you today?"
    return state

def sub_classify_node(state: SupportState) -> SupportState:
    sub_classification = classify_relevant_query(state["message"])
    state["sub_classification"] = sub_classification
    return state

def check_memory_node(state: SupportState) -> SupportState:
    """Pass-through node - memory is now handled by extract_memory_node"""
    return state

def search_vector_db_node(state: SupportState) -> SupportState:
    if state["context"] == "from_memory":
        return state
    
    docs = search_company_info(state["message"])
    
    if not docs:
        state["response"] = "I don't have information on that."
        return state
    
    context = "\n".join([doc.page_content for doc in docs])
    memory_context = state["memory"].get_memory_json()

    llm = get_llm()
    prompt = f"""Based ONLY on the following information, answer the user's question.Reply in ONLY ONE language (English OR Urdu).
Use the SAME language as the user's question.
Do NOT include translations.
If the information doesn't contain the answer, say "I don't have information on that."
Be very very Empathetic and do not need to stay too concise

Customer Context (what we know about this user):
{memory_context}

Context:
{context}

Question: {state['message']}

Answer:"""
    
    response = llm.invoke(prompt)
    state["response"] = response.content
    
    return state

def query_database_node(state: SupportState) -> SupportState:
    order_data = get_order_info(state["user_id"], state["message"])
    
    if not order_data:
        state["response"] = "I couldn't find any order information for your account."
        return state
    
    memory_context = state["memory"].get_memory_json()
    llm = get_llm()
    prompt = f"""Based ONLY on the following order data, answer the user's question.
Be specific and use the actual data provided.

Customer Context (what we know about this user):
{memory_context}

Order Data:
{order_data}

Question: {state['message']}

Answer:"""
    
    response = llm.invoke(prompt)
    state["response"] = response.content
    
    return state

def route_after_classification(state: SupportState) -> str:
    classification = state["classification"]
    
    if classification == "greeting_smalltalk":
        return "greeting"
    elif classification == "irrelevant":
        return "irrelevant"
    else:
        return "sub_classify"

def route_after_sub_classification(state: SupportState) -> str:
    sub_classification = state["sub_classification"]
    
    if sub_classification == "company_info":
        return "check_memory"
    else:
        return "query_database"

def route_after_memory(state: SupportState) -> str:
    """Always go to search_vector since old memory system is removed"""
    return "search_vector"

def create_support_graph():
    workflow = StateGraph(SupportState)
    
    # Add nodes
    workflow.add_node("classify", classify_node)
    workflow.add_node("extract_memory", extract_memory_node)
    workflow.add_node("greeting", handle_greeting)
    workflow.add_node("irrelevant", handle_irrelevant)
    workflow.add_node("sub_classify", sub_classify_node)
    workflow.add_node("check_memory", check_memory_node)
    workflow.add_node("search_vector", search_vector_db_node)
    workflow.add_node("query_database", query_database_node)
    
    # Set entry point
    workflow.set_entry_point("classify")
    
    # Connect classify to extract_memory
    workflow.add_edge("classify", "extract_memory")
    
    # Add conditional edges from extract_memory
    workflow.add_conditional_edges(
        "extract_memory",
        route_after_classification,
        {
            "greeting": "greeting",
            "irrelevant": "irrelevant",
            "sub_classify": "sub_classify"
        }
    )
    
    workflow.add_conditional_edges(
        "sub_classify",
        route_after_sub_classification,
        {
            "check_memory": "check_memory",
            "query_database": "query_database"
        }
    )
    
    workflow.add_conditional_edges(
        "check_memory",
        route_after_memory,
        {
            "end": END,
            "search_vector": "search_vector"
        }
    )
    
    # Add edges to END
    workflow.add_edge("greeting", END)
    workflow.add_edge("irrelevant", END)
    workflow.add_edge("search_vector", END)
    workflow.add_edge("query_database", END)
    
    return workflow.compile()