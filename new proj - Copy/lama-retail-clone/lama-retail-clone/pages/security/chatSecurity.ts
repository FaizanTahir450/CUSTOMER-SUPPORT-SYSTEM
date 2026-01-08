import DOMPurify from "dompurify";

/* ===============================
   SECURITY CONFIG
================================ */
const SECURITY_CONFIG = {
  MAX_MESSAGE_LENGTH: 500,
  MIN_MESSAGE_INTERVAL_MS: 1500,
  BLOCKED_PATTERNS: [
    /<script>/i,
    /password/i,
    /api[_-]?key/i,
    /token/i,
    /authorization/i,
  ],
};

/* ===============================
   RATE LIMITER (CLIENT SIDE)
================================ */
let lastMessageTime = 0;

const canSendMessage = (): boolean => {
  const now = Date.now();
  if (now - lastMessageTime < SECURITY_CONFIG.MIN_MESSAGE_INTERVAL_MS) {
    return false;
  }
  lastMessageTime = now;
  return true;
};

/* ===============================
   INPUT VALIDATION
================================ */
const validateInput = (input: string): string | null => {
  if (!input.trim()) {
    return "Empty message is not allowed.";
  }

  if (input.length > SECURITY_CONFIG.MAX_MESSAGE_LENGTH) {
    return `Message too long. Max ${SECURITY_CONFIG.MAX_MESSAGE_LENGTH} characters allowed.`;
  }

  for (const pattern of SECURITY_CONFIG.BLOCKED_PATTERNS) {
    if (pattern.test(input)) {
      return "Sensitive or unsafe content detected. Please rephrase.";
    }
  }

  return null;
};

/* ===============================
   OUTPUT SANITIZATION (XSS)
================================ */
export const sanitizeOutput = (text: string): string => {
  return DOMPurify.sanitize(text, { ALLOWED_TAGS: [] });
};

/* ===============================
   MAIN SECURE CHAT HANDLER
================================ */
export const sendSecureChatMessage = async (
  message: string,
  addMessage: (text: string, sender: "user" | "ai") => void,
  setLoading: (value: boolean) => void
) => {
  // Input checks
  const validationError = validateInput(message);
  if (validationError) {
    addMessage(validationError, "ai");
    return;
  }

  // Rate limiting
  if (!canSendMessage()) {
    addMessage("You're sending messages too fast. Please slow down.", "ai");
    return;
  }

  setLoading(true);

  try {
    // throw new Error("SECURITY LAYER HIT");

    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error("Server error");
    }

    const data = await response.json();
    addMessage(sanitizeOutput(data.response), "ai");

  } catch {
    addMessage("Unable to connect to support right now. Please try again later.", "ai");
  } finally {
    setLoading(false);
  }
};
