const ROUTER_BASE_URL = import.meta.env.VITE_ROUTER_URL || '';

const classifyAndRouteQuery = async (query: string) => {
  try {
    const classifyResponse = await fetch(`${ROUTER_BASE_URL}/classify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });

    const { classification } = await classifyResponse.json();

    const normalized = (classification || '').trim().toLowerCase();
    const cleaned = normalized
      .replace(/[^a-z/ ]+/g, '') // drop punctuation like trailing slashes
      .replace(/\/+$/, '')
      .replace(/\s+/g, ' ')
      .trim();

    const isPolicy = cleaned === 'policy/faq' || cleaned === 'policy' || cleaned.includes('policy');
    const isDb =
      cleaned === 'database/transactional query' ||
      cleaned === 'database transactional query' ||
      cleaned.includes('database');

    const isSmallTalk = cleaned === 'small talk' || cleaned.includes('small');

    const agentEndpoint = isPolicy
      ? '/agent1'
      : isDb
      ? '/agent2'
      : isSmallTalk
      ? '/agent1'
      : null;

    if (!agentEndpoint) {
      return "Sorry, the query can't be resolved.";
    }

    const agentResponse = await fetch(`${ROUTER_BASE_URL}${agentEndpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });

    if (!agentResponse.ok) {
      const text = await agentResponse.text();
      return `Agent error (${agentResponse.status}): ${text || 'No details'}`;
    }

    const { response } = await agentResponse.json();
    return response || 'No response from agent.';
  } catch (error) {
    console.error('Error:', error);
    return 'Unable to process the query.';
  }
};
export { classifyAndRouteQuery };