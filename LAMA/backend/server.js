const express = require('express');
const cors = require('cors');
const classifyRouter = require('./routes/classify');
const { router: agent1Router } = require('./routes/agent1');
const { router: agent2Router } = require('./routes/agent2');
const config = require('./config');

const app = express();
const PORT = config.PORT;

// Middleware
app.use((req, _res, next) => {
  console.log(`${new Date().toISOString()} ${req.method} ${req.url}`);
  next();
});
app.use(cors()); // Enable Cross-Origin Resource Sharing
app.use(express.json()); // Parse JSON body
app.use(express.urlencoded({ extended: true })); // Parse x-www-form-urlencoded body

// Routing
app.use('/classify', classifyRouter); // Query classification
app.use('/agent1', agent1Router);     // Policy/FAQ routing
app.use('/agent2', agent2Router);     // Database/Transactional routing

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running at http://localhost:${PORT}`);
});