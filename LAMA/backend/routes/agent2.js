const express = require('express');
const axios = require('axios');
const config = require('../config');

const router = express.Router();

const handleQuery = async (query) => {
  const resp = await axios.post(`${config.AGENT2_URL}/api/query`, { question: query });
  const data = resp.data || {};
  if (data.type === 'sql_result') {
    return { response: data.explanation || JSON.stringify(data.results) };
  }
  return { response: data.message || data.content || 'No response from agent 2.' };
};

router.post('/', async (req, res) => {
  const { query } = req.body;
  if (!query || typeof query !== 'string') {
    return res.status(400).send({ error: 'Invalid or empty query provided.' });
  }

  try {
    const result = await handleQuery(query);
    res.send(result);
  } catch (error) {
    console.error('Agent 2 Error:', error);
    res.status(500).send({ error: error.message || 'Agent 2 failed.' });
  }
});

module.exports = { handleQuery, router };