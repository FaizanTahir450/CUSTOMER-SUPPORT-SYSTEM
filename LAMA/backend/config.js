const dotenv = require('dotenv');

// Load environment variables from .env file
dotenv.config();

module.exports = {
  PORT: process.env.PORT || 8001,
  AGENT1_URL: process.env.AGENT1_URL || 'http://localhost:8000',
  AGENT2_URL: process.env.AGENT2_URL || 'http://localhost:5000',
  GEMINI_API_URL:
    process.env.GEMINI_API_URL ||
    'https://generativelanguage.googleapis.com/v1beta',
  GEMINI_MODEL: process.env.GEMINI_MODEL || 'gemini-2.5-flash',
  GEMINI_API_KEY: process.env.GEMINI_API_KEY || 'AIzaSyBTTh5vhhIDPuTSvTWoj9K52W4OGEPcGeA',
};