
import { GoogleGenAI } from "@google/genai";

const SYSTEM_INSTRUCTION = `
You are the official customer support AI for LUMINA, a high-end sustainable clothing brand.
Tone: Professional, elegant, helpful, and concise.
Knowledge Base:
- Return Policy: 30-day returns for unworn items with tags attached.
- Shipping: Free standard shipping on orders over $150. International shipping available.
- Sustainability: We use organic cotton, recycled polyester, and ethical factories in Portugal and Italy.
- Order Status: Ask the user for their order number (e.g., #LUM-12345) to "check" (simulated).
- Materials: Organic cotton, linen, recycled denim, and certified silk.
If you don't know something, offer to connect them to a human representative.
`;

export class GeminiService {
  /**
   * Generates a response from the Gemini AI model.
   * Following @google/genai guidelines:
   * 1. Instantiates GoogleGenAI immediately before the API call to ensure fresh configuration.
   * 2. Uses process.env.API_KEY directly.
   * 3. Uses 'gemini-3-flash-preview' for general support tasks.
   * 4. Accesses the .text property of GenerateContentResponse directly.
   */
  async generateResponse(message: string): Promise<string> {
    try {
      const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
      const response = await ai.models.generateContent({
        model: 'gemini-3-flash-preview',
        contents: message,
        config: {
          systemInstruction: SYSTEM_INSTRUCTION,
        },
      });

      // The .text property directly returns the generated string.
      return response.text || "I'm sorry, I'm having trouble processing your request right now.";
    } catch (error) {
      console.error("Gemini Error:", error);
      throw new Error("Failed to reach AI support service.");
    }
  }
}
