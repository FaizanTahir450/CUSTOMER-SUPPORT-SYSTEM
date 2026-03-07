# graph.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from app.services.classifier import classify_query, classify_relevant_query
from app.services.memory import LLMCustomerSupportMemory
from app.services.vector_store import search_company_info
from app.models.database import get_orders, cancel_order
from app.services.llm import get_llm
import json
import logging

logger = logging.getLogger(__name__)

class SupportState(TypedDict):
    user_id: str
    message: str
    response: str
    classification: str
    sub_classification: str
    context: str
    memory: LLMCustomerSupportMemory
    conversation_history: List[dict]  # Full conversation history for LLM context

def classify_node(state: SupportState) -> SupportState:
    classification = classify_query(state["message"])
    state["classification"] = classification
    logger.debug(f"Classification node: {classification}")
    return state

def extract_memory_node(state: SupportState) -> SupportState:
    """Extract facts from user message and update memory"""
    memory = state["memory"]
    memory.update_memory(state["message"])
    # Update conversation_history in state
    state["conversation_history"] = memory.get_conversation_history()
    logger.debug(f"Memory updated for user {state['user_id']}")
    return state

def _build_conversation_context(conversation_history: List[dict], max_turns: int = 6) -> str:
    """Format recent conversation for LLM context."""
    recent = conversation_history[-max_turns:] if conversation_history else []
    if not recent:
        return ""
    
    context_lines = []
    for turn in recent:
        role_label = "Customer" if turn["role"] == "user" else "Sophia (support)"
        context_lines.append(f"{role_label}: {turn['content']}")
    
    return "Recent conversation context:\n" + "\n".join(context_lines) + "\n"

def handle_greeting(state: SupportState) -> SupportState:
    memory_context = state["memory"].get_memory_json()
    conversation_context = _build_conversation_context(state["conversation_history"])
    
    llm = get_llm()
    prompt = (
        f"You are 'Sophia', Lama retail's customer support agent. "
        f"Respond politely and briefly. "
        f"Choose ONLY ONE language (English OR Urdu), not both. "
        f"Reply in the SAME language as the user's message. "
        f"Do NOT bring up past complaints, orders, or issues from memory unless the user asks. "
        f"\n{conversation_context}"
        f"\nCustomer context (background only — do NOT reference unless directly asked): {memory_context}\n"
        f"User message: {state['message']}"
    )
    
    response = llm.invoke(prompt)
    state["response"] = response.content
    state["memory"].add_assistant_message(state["response"])
    state["conversation_history"] = state["memory"].get_conversation_history()
    logger.info(f"Greeting handled for user {state['user_id']}")
    return state

def handle_irrelevant(state: SupportState) -> SupportState:
    state["response"] = "I'm a customer support assistant. I can ONLY help you with questions about our company, services, or your orders. How can I assist you today?"
    state["memory"].add_assistant_message(state["response"])
    state["conversation_history"] = state["memory"].get_conversation_history()
    logger.debug(f"Irrelevant query handled for user {state['user_id']}")
    return state

def sub_classify_node(state: SupportState) -> SupportState:
    sub_classification = classify_relevant_query(state["message"])
    state["sub_classification"] = sub_classification
    logger.debug(f"Sub-classification node: {sub_classification}")
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
        state["memory"].add_assistant_message(state["response"])
        state["conversation_history"] = state["memory"].get_conversation_history()
        return state
    
    context = "\n".join([doc.page_content for doc in docs])
    memory_context = state["memory"].get_memory_json()
    conversation_context = _build_conversation_context(state["conversation_history"])

    llm = get_llm()
    prompt = (
        f"""Based ONLY on the following information, answer the user's question.
Reply in ONLY ONE language (English OR Urdu).
Use the SAME language as the user's question.
Do NOT include translations.
If the information doesn't contain the answer, say "I don't have information on that."
Be helpful and clear.

IMPORTANT RULES for using customer context:
- The customer context below is background information only. Do NOT mention it, reference it, or bring it up unless the customer explicitly asks about their past interactions.
- Answer the current question directly. Do not bring up past complaints, emotions, or order history unprompted.
- Only greet the customer by name if this is the very first message in the conversation.

{conversation_context}

Customer Context (background only — do NOT reference unless directly asked):
{memory_context}

Company Information:
{context}

Question: {state['message']}

Answer:"""
    )
    
    response = llm.invoke(prompt)
    state["response"] = response.content
    state["memory"].add_assistant_message(state["response"])
    state["conversation_history"] = state["memory"].get_conversation_history()
    logger.info(f"Vector DB search completed for user {state['user_id']}")
    
    return state

def _parse_llm_json(raw: str) -> dict:
    """Strip markdown fences if present and parse JSON. Returns {} on failure."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1].strip()
        if raw.startswith("json"):
            raw = raw[4:].strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def query_database_node(state: SupportState) -> SupportState:
    # ── 1. Load all orders for this user ────────────────────────────────────
    orders, err = get_orders(state["user_id"])
    if err:
        state["response"] = "I couldn't fetch your orders right now. Please try again later."
        logger.error(f"Error fetching orders for user {state['user_id']}: {err}")
        state["memory"].add_assistant_message(state["response"])
        state["conversation_history"] = state["memory"].get_conversation_history()
        return state
    if not orders:
        state["response"] = "I couldn't find any order information for your account."
        state["memory"].add_assistant_message(state["response"])
        state["conversation_history"] = state["memory"].get_conversation_history()
        return state

    # Format orders for the LLM prompt
    orders_text = "\n".join(
        f"- Order ID: {o['order_id']} | Status: {o['status']} | "
        f"Total: ${float(o['total']):.2f} | "
        f"Date: {o['created_at'].strftime('%Y-%m-%d') if hasattr(o['created_at'], 'strftime') else str(o['created_at'])}"
        for o in orders
    )

    memory_context = state["memory"].get_memory_json()
    conversation_context = _build_conversation_context(state["conversation_history"])
    llm = get_llm()

    # ── 2. Single LLM call: answer OR invoke cancel tool ────────────────────
    prompt = f"""You are Sophia, Lama Retail's customer support agent.
You have access to one tool: cancel_order(order_id).

Given the customer's orders and their message, decide what to do:

A) If the customer is asking about order status, history, or any general order info:
   Respond with a plain text answer using the order data below. Be empathetic and specific.

B) If the customer wants to cancel an order:
   - Only orders with status 'pending' or 'processing' can be cancelled.
   - If cancellable, respond with ONLY this JSON (no extra text):
     {{"tool": "cancel_order", "order_id": "<order_id>"}}
   - If NOT cancellable, respond with plain text explaining why.

C) If the customer wants to reorder or place a new order:
   Respond with plain text telling them to place a new order through the website.

IMPORTANT: Answer the current question directly. Do NOT bring up past complaints,
emotions, or context from memory unless the customer explicitly asks about them.

{conversation_context}

Customer context (background only — do NOT reference unless directly asked):
{memory_context}

Customer orders:
{orders_text}

Customer message: {state['message']}
"""

    raw_response = llm.invoke(prompt).content.strip()

    # ── 3. Check if LLM wants to call the cancel tool ───────────────────────
    tool_call = _parse_llm_json(raw_response)

    if tool_call.get("tool") == "cancel_order":
        order_id = str(tool_call.get("order_id", "")).strip()

        if not order_id:
            state["response"] = "I wasn't able to determine which order to cancel. Could you please confirm the order ID?"
            state["memory"].add_assistant_message(state["response"])
            state["conversation_history"] = state["memory"].get_conversation_history()
            return state

        # Verify the order actually belongs to this user before cancelling
        valid_ids = {str(o["order_id"]) for o in orders}
        if order_id not in valid_ids:
            state["response"] = "I couldn't find that order on your account."
            state["memory"].add_assistant_message(state["response"])
            state["conversation_history"] = state["memory"].get_conversation_history()
            return state

        success, error = cancel_order(order_id, state["user_id"])
        if success:
            state["response"] = f"✅ Order {order_id} has been successfully cancelled."
            logger.info(f"Order {order_id} cancelled for user {state['user_id']}")
        else:
            state["response"] = f"⚠️ I wasn't able to cancel order {order_id}: {error}"
            logger.warning(f"Failed to cancel order {order_id} for user {state['user_id']}: {error}")
        
        state["memory"].add_assistant_message(state["response"])
        state["conversation_history"] = state["memory"].get_conversation_history()
        return state

    # ── 4. Plain text response (info query, reorder, or refusal) ────────────
    state["response"] = raw_response
    state["memory"].add_assistant_message(state["response"])
    state["conversation_history"] = state["memory"].get_conversation_history()
    logger.info(f"Database query completed for user {state['user_id']}")
    return state

def route_after_classification(state: SupportState) -> str:
    classification = state["classification"]
    
    if classification == "greeting_smalltalk":
        return "greeting"
    elif classification == "irrelevant":
        return "irrelevant"
    else:
        return "extract_memory"

def route_after_sub_classification(state: SupportState) -> str:
    sub_classification = state["sub_classification"]
    
    if sub_classification == "company_info":
        return "check_memory"
    else:
        return "query_database"

def create_support_graph():
    """Build the support graph with conversation history support."""
    graph = StateGraph(SupportState)
    
    graph.add_node("classify", classify_node)
    graph.add_node("greeting", handle_greeting)
    graph.add_node("irrelevant", handle_irrelevant)
    graph.add_node("extract_memory", extract_memory_node)
    graph.add_node("sub_classify", sub_classify_node)
    graph.add_node("check_memory", check_memory_node)
    graph.add_node("search_vector_db", search_vector_db_node)
    graph.add_node("query_database", query_database_node)
    
    graph.set_entry_point("classify")
    
    graph.add_conditional_edges(
        "classify",
        route_after_classification,
        {
            "greeting": "greeting",
            "irrelevant": "irrelevant",
            "extract_memory": "extract_memory"
        }
    )
    
    graph.add_edge("extract_memory", "sub_classify")
    
    graph.add_conditional_edges(
        "sub_classify",
        route_after_sub_classification,
        {
            "check_memory": "check_memory",
            "query_database": "query_database"
        }
    )
    
    graph.add_edge("check_memory", "search_vector_db")
    
    graph.add_edge("greeting", END)
    graph.add_edge("irrelevant", END)
    graph.add_edge("search_vector_db", END)
    graph.add_edge("query_database", END)
    
    logger.info("Support graph created successfully with conversation history support")
    return graph.compile()