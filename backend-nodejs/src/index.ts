import "dotenv/config";
import express from 'express';
import helmet from 'helmet';
import {authRouter} from './routes/auth';
import {ensureSchema,pool} from './lib/db';
import {errorHandler} from './middleware/errorHandler';
import {httpLogger, logger} from './lib/logger';
import {requestIdMiddleware} from './middleware/requestId';
import {generalLimiter} from './middleware/rateLimiter';
import {validateEnvironment} from './lib/envValidation';
import cors from 'cors';

// Validate environment variables before starting
validateEnvironment();

const app = express();
const PORT = process.env.PORT || 4000;
app.use(express.json());
app.use(cors());
app.use(helmet()); // Security headers
app.use(requestIdMiddleware); // Add request ID for tracing
app.use(httpLogger); // HTTP logging
app.use(generalLimiter); // Rate limiting


app.get('/health',(req,res)=>{
    res.status(200).json({status:'ok'});
})

app.use('/api/auth',authRouter);
app.use(errorHandler);

const server = app.listen(PORT, async() => {
    try {
        // Ensure database and schema exist first
        await ensureSchema();
        logger.info('Database schema ensured');
        
        // Then test the connection
        await pool.getConnection().then(conn => {
            logger.info('Connected to MySQL database');
            conn.release();
        }).catch(err => {
            logger.error(err, 'Error connecting to MySQL database');
        })
        
        logger.info({ port: PORT }, 'Server is running');
    } catch(err) {
        logger.error(err, 'Error during server startup');
        process.exit(1);
    }
});

// Graceful shutdown
process.on('SIGTERM', async () => {
    logger.info('SIGTERM received, shutting down gracefully');
    server.close(async () => {
        logger.info('Server closed');
        await pool.end();
        logger.info('Database connection closed');
        process.exit(0);
    });
});

process.on('SIGINT', async () => {
    logger.info('SIGINT received, shutting down gracefully');
    server.close(async () => {
        logger.info('Server closed');
        await pool.end();
        logger.info('Database connection closed');
        process.exit(0);
    });
});