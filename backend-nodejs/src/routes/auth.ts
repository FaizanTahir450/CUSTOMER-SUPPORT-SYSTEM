import {Router } from 'express';
import { signupHandler  }  from '../controllers/signup';
import { loginhandler } from '../controllers/login';
import { sign } from 'crypto';

export const authRouter = Router();

authRouter.post('/signup',signupHandler);
authRouter.post('/login',loginhandler);
