const agent1Handler = require('./agent1'); // Handler for RAG queries
const agent2Handler = require('./agent2'); // Handler for SQL queries

const routeQuery = async (query, classification) => {
  switch (classification) {
    case 'Small Talk':
      return { response: "This is a small talk query. How can I assist more?" };

    case 'Policy/FAQ':
      return await agent1Handler.handleQuery(query);

    case 'Database/Transactional Query':
      return await agent2Handler.handleQuery(query);

    case 'Out of Context':
      return { response: "Sorry, I can't assist with that query." };

    default:
      throw new Error('Unknown classification.');
  }
};

module.exports = { routeQuery };