import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { logger } from '../lib/logger';

export interface AuthRequest extends Request {
  user?: {
    id: string;
    email: string;
    role?: string;
  };
}

/**
 * Auth middleware - verifies JWT token and attaches user to request
 */
export function requireAuth(req: AuthRequest, res: Response, next: NextFunction) {
  const log = (req as any).log || logger;
  
  try {
    const token = req.headers.authorization?.split(' ')[1];
    
    if (!token) {
      log?.warn({ path: req.path }, 'Auth failed: no token provided');
      return res.status(401).json({
        error: { code: 'unauthorized', message: 'No token provided' }
      });
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as any;
    
    req.user = {
      id: decoded.sub,
      email: decoded.email,
      role: decoded.role
    };

    log?.debug({ userId: req.user.id }, 'Auth successful');
    next();
  } catch (err) {
    log?.warn({ err }, 'Auth failed: invalid token');
    return res.status(401).json({
      error: { code: 'unauthorized', message: 'Invalid or expired token' }
    });
  }
}

/**
 * Optional auth middleware - attaches user if token is valid, but doesn't require it
 */
export function optionalAuth(req: AuthRequest, res: Response, next: NextFunction) {
  const token = req.headers.authorization?.split(' ')[1];
  
  if (token) {
    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET!) as any;
      req.user = {
        id: decoded.sub,
        email: decoded.email,
        role: decoded.role
      };
    } catch (err) {
      // Silently fail - token is optional
    }
  }
  
  next();
}
