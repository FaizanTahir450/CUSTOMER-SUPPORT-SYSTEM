# classifiers.py
from llm import get_llm

def classify_query(message: str) -> str:
    """
    First-level classification: Determines if the query is greeting/smalltalk, 
    irrelevant, or relevant to customer support.
    """
    llm = get_llm()
    
    prompt = f"""Classify the following user message into exactly ONE category:

- "greeting_smalltalk" - Greetings, introductions, personal conversation, casual chat, remembering names
  Examples: "hi", "hello", "how are you", "my name is John", "do you remember my name?", "good morning", "what's your name?", "nice to meet you"

- "irrelevant" - Completely off-topic content unrelated to any aspect of customer support
  Examples: "what's the weather?", "tell me a joke", "who won the game?", "write me a poem", "what's 2+2?"

- "relevant" - ANY question about company, services, policies, products, orders, complaints, issues, returns, refunds
  Examples: "what are your hours?", "I have a problem with my order", "how do I return something?", "my order is defective", "where is my package?", "I want to cancel"

User message: {message}

Respond with ONLY the category name, nothing else."""

    response = llm.invoke(prompt)
    classification = response.content.strip().lower()
    
    if classification not in ["greeting_smalltalk", "irrelevant", "relevant"]:
        classification = "irrelevant"
    
    return classification

def classify_relevant_query(message: str) -> str:
    """
    Second-level classification: Routes relevant queries to either RAG (company info/policies)
    or Database (specific order lookups).
    
    KEY DISTINCTION:
    - company_info: Needs policy/procedure information from documents (even if about orders)
    - order_related: Needs specific order data from database (tracking, status, details)
    """
    llm = get_llm()
    
    prompt = f"""Classify the following user message into exactly ONE category:

- "company_info" - Questions needing POLICIES, PROCEDURES, or GENERAL INFORMATION including:
  * Company information, hours, locations, contact info
  * Return/refund policies and procedures
  * Shipping policies and general timeframes
  * Product information and FAQs
  * How-to questions about processes
  * Complaints about product quality/defects (needs return policy)
  * General questions about services
  Examples: "What's your return policy?", "How do I return a defective item?", "What are your business hours?", 
            "My order arrived damaged, what do I do?", "Do you ship internationally?", "How long does shipping take?"

- "order_related" - Questions needing SPECIFIC ORDER DATA from the database:
  * Order status/tracking ("Where is my order?")
  * Specific order details ("What did I order?")
  * Order history lookups
  * Cancellation of a specific order
  Examples: "Where is my order?", "Track order #12345", "What's my order status?", "When will my order arrive?",
            "Cancel my order", "What did I order last week?"

IMPORTANT: If the user has a problem with an order (defective, damaged, wrong item), classify as "company_info" 
because they need the return/refund POLICY, not order data.

User message: {message}

Respond with ONLY the category name, nothing else."""

    response = llm.invoke(prompt)
    classification = response.content.strip().lower()
    
    if classification not in ["company_info", "order_related"]:
        classification = "company_info"
    
    return classification