import { Request, Response, NextFunction } from 'express';
import { z } from 'zod';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { supabase } from '../lib/db';
import { logger } from '../lib/logger';

const loginschema = z.object({
    email:
        z.string()
            .trim()
            .toLowerCase()
            .email(),
    password:
        z.string()
            .min(1)
});

export async function loginhandler(req: Request, res: Response, next: NextFunction) {
    const log = (req as any).log || logger;
    try {
        log?.debug({ email: req.body.email }, 'Login attempt');
        const parsed = loginschema.safeParse(req.body);
        if (!parsed.success) {
            log?.warn({ errors: parsed.error.issues }, 'Login validation failed');
            return res.status(400).json({
                error: { code: "validation error", message: parsed.error.issues[0]?.message || 'invalid input' }
            });
        }
        const { email, password } = parsed.data;
        
        // GET USER BY EMAIL
        const { data: user, error: selectError } = await supabase
            .from('users')
            .select('id, email, password_hash, name, role, created_at')
            .eq('email', email)
            .maybeSingle();
        
        if (selectError && selectError.code !== 'PGRST116') {
            throw selectError;
        }
        
        if (!user) {
            log?.warn({ email }, 'Login failed: user not found');
            return res.status(401).json({
                error: { code: "invalid credentials", message: "Invalid email or password" }
            })
        }
        
        // VERIFY PASSWORD
        const match = await bcrypt.compare(password, user.password_hash);
        if (!match) {
            log?.warn({ email }, 'Login failed: invalid password');
            return res.status(401).json({ 
                error: { code: "invalid credentials", message: "Invalid email or password" } 
            })
        }

        // GENERATE TOKEN
        const token = jwt.sign(
            { sub: user.id, email: user.email, role: user.role },
            process.env.JWT_SECRET!,
            { expiresIn: '7d' }
        );
        
        log?.info({ userId: user.id, email: user.email }, 'Login successful');
        return res.status(200).json({
            user: { id: user.id, email: user.email, name: user.name, role: user.role, createdAt: user.created_at },
            token
        });

    }
    catch (err) {
        log?.error({ err }, 'Login error: unexpected error');
        return next(err);
    }
}

