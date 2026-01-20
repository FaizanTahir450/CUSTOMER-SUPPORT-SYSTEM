const axios = require('axios');
const config = require('../config');

const classifyQuery = async (query) => {
  try {
    const prompt = `
        You are a robust query classifier for a customer support assistant. 
        Your job is to **classify user queries** into **one of the predefined categories**:
          - **Small Talk**: Casual greetings or conversational questions unrelated to customer support (e.g.,"hi", "Hello, how are you?", "Nice to meet you!", "What's the weather today?").
          - **Policy/FAQ**: Questions related to company policies, orders, returns, product details, or frequently asked questions (e.g., "How do I return an item?", "What is the shipping policy?", "What is the warranty on this product?").
          - **Database/Transactional Query**: Queries requiring retrieving or updating transactional data (e.g., "Get my latest order details", "Cancel my subscription", "When will my product arrive?").
          - **Out of Context**: Any input that is irrelevant to the assistant's purpose or cannot be understood meaningfully (e.g., "asdfgh", "Tell me about quantum physics").

        Instructions:
        - Output **one category only**.
        - If you cannot confidently classify the query into any category, respond with **"Out of Context"**.
        - Avoid making assumptions if the query lacks sufficient information.

        Example queries and their categories:
        - Query: "Hello, good morning!" → Response: "Small Talk"
        - Query: "How can I track my order?" → Response: "Policy/FAQ"
        - Query: "Fetch my invoice for product ID 123" → Response: "Database/Transactional Query"
        - Query: "What is the capital of France?" → Response: "Out of Context"

        Classify the following user query:
        "${query}"

        Respond with one category only.
    `;

    const baseUrl = (config.GEMINI_API_URL || '').replace(/\/$/, '');
    const modelsBase = baseUrl.includes('/models') ? baseUrl : `${baseUrl}/models`;
    const model = config.GEMINI_MODEL || 'gemini-2.5-flash';
    const url = `${modelsBase}/${model}:generateContent?key=${config.GEMINI_API_KEY}`;

    const response = await axios.post(
      url,
      {
        contents: [
          {
            role: 'user',
            parts: [{ text: prompt }],
          },
        ],
        generationConfig: {
          temperature: 0,
          maxOutputTokens: 50,
        },
      },
      { timeout: 5000 }
    );

    const text = response.data?.candidates?.[0]?.content?.parts?.[0]?.text;
    return text?.trim() || 'Out of Context';
  } catch (error) {
    const status = error?.response?.status;
    if (status === 429) {
      console.warn('Gemini rate limit hit; defaulting classification to Out of Context');
      return 'Out of Context';
    }
    const detail = error?.response?.data ? JSON.stringify(error.response.data) : error?.message;
    console.error('Gemini Classification Error:', detail || error);
    return 'Out of Context';
  }
};

module.exports = { classifyQuery };