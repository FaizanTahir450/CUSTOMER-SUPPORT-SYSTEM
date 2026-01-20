const express = require('express');
const { classifyQuery } = require('../services/llmClassifier');
const router = express.Router();

// Endpoint for Query Classification
router.post('/', async (req, res) => {
  const { query } = req.body;

  if (!query || typeof query !== 'string') {
    return res.status(400).send({ error: 'Invalid query input.' });
  }

  try {
    const classification = await classifyQuery(query);
    console.log('classification result', { query, classification });
    res.send({ classification });
  } catch (error) {
    res.status(500).send({ error: error.message });
  }
});

module.exports = router;