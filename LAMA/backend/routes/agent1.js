const express = require('express');
const axios = require('axios');
const config = require('../config');

const router = express.Router();

const handleQuery = async (query) => {
  const resp = await axios.post(`${config.AGENT1_URL}/chat`, { message: query });
  return { response: resp.data?.response || 'No response from agent 1.' };
};

router.post('/', async (req, res) => {
  const { query } = req.body;
  if (!query) return res.status(400).send({ error: 'Invalid query.' });

  try {
    const result = await handleQuery(query);
    res.send(result);
  } catch (error) {
    const status = error?.response?.status;
    const data = error?.response?.data;
    const code = error?.code;
    console.error('Agent1 proxy error', { status, code, message: error?.message, data });
    res
      .status(500)
      .send({ error: error.message || 'Agent 1 failed.', code: code || undefined, details: data || undefined });
  }
});

module.exports = { handleQuery, router };