import {Request,Response,NextFunction} from 'express';
import { logger } from '../lib/logger';

interface CustomError extends Error {
    status?: number;
    code?: string;
}

export function errorHandler(err: CustomError, req:Request, res:Response, next:NextFunction){
    const log = (req as any).log || logger;
    
    const status = err.status || 500;
    const code = err.code || 'internal_server_error';
    const message = process.env.NODE_ENV === 'production' 
        ? 'An unexpected error occurred' 
        : err.message || 'An unexpected error occurred';

    // Log the error with full details
    log?.error({
        err,
        status,
        code,
        path: req.path,
        method: req.method,
    }, `${req.method} ${req.path} - Error occurred`);

    return res.status(status).json({
        error: {
            code,
            message,
            ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
        }
    });
}