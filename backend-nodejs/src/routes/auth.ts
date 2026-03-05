import {Router } from 'express';
import { signupHandler  }  from '../controllers/signup';
import { loginhandler } from '../controllers/login';
import { resetPasswordHandler, requestPasswordResetHandler } from '../controllers/passwordReset';
import { authLimiter, passwordResetLimiter } from '../middleware/rateLimiter';

export const authRouter = Router();

authRouter.post('/signup', authLimiter, signupHandler);
authRouter.post('/login', authLimiter, loginhandler);
authRouter.post('/forget-password', passwordResetLimiter, requestPasswordResetHandler);
authRouter.post('/reset-password', passwordResetLimiter, resetPasswordHandler);
