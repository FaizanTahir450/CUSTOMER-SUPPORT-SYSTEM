import { Request, Response, NextFunction } from 'express'
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { z } from 'zod';
import { v4 as uuidv4 } from 'uuid';
import { supabase } from '../lib/db';
import { logger } from '../lib/logger';

const signupSchema = z.object({
    email:
        z.string()
            .trim()
            .toLowerCase()
            .email(),
    password:
        z.string()
            .min(8, 'Password must be atleast 8 characters long')
            .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
            .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
            .regex(/[0-9]/, 'Password must contain at least one number')
            .regex(/[@$!%*?&]/, 'Password must contain at least one special character (@$!%*?&)'),
    name:
        z.string()
            .trim()
            .max(100, 'Name must be less than 100 characters')
            .optional()
            .nullable()

});

export async function signupHandler(req: Request, res: Response, next: NextFunction) {
    const log = (req as any).log || logger;
    try {
        log?.debug({ email: req.body.email }, 'Signup attempt');
        const parsed = signupSchema.safeParse(req.body);
        if (!parsed.success) {
            log?.warn({ errors: parsed.error.issues }, 'Signup validation failed');
            return res.status(400).json({
                error: { code: "validation error", message: parsed.error.issues[0]?.message || 'Invalid input' }
            });
        }
        const { email, password, name } = parsed.data;
        log?.debug({ email }, 'Checking if user already exists');
        
        // CHECK IF USER EXISTS
        const { data: existingUser, error: checkError } = await supabase
            .from('users')
            .select('id')
            .eq('email', email)
            .maybeSingle();
        
        if (checkError && checkError.code !== 'PGRST116') {
            throw checkError;
        }
        
        if (existingUser) {
            log?.warn({ email }, 'Signup failed: email already exists');
            return res.status(409).json({
                error: { code: "Email exists", message: "An account with this email already exists" }
            })
        };
        
        log?.debug({ email }, 'Hashing password');
        const passwordHash = await bcrypt.hash(password, 12);
        const userId = uuidv4();
        
        log?.debug({ email }, 'Inserting new user into database');
        
        // INSERT NEW USER
        const { data: insertResult, error: insertError } = await supabase
            .from('users')
            .insert([{
                id: userId,
                email: email,
                password_hash: passwordHash,
                name: name || null,
                role: 'user'
            }])
            .select();
        
        if (insertError) {
            log?.error({ insertError, email }, 'Failed to insert user');
            throw insertError;
        }
        
        log?.debug({ email }, 'User created, retrieving user data');
        
        // RETRIEVE NEWLY CREATED USER
        const { data: users, error: selectError } = await supabase
            .from('users')
            .select('id, email, name, role, created_at')
            .eq('email', email)
            .single();
        
        if (selectError || !users) {
            log?.error({ email, selectError }, 'Signup failed: user select failed');
            throw new Error('User insert verification failed');
        }
        
        const user = users;
        
        log?.debug({ email }, 'Generating JWT token');
        const token = jwt.sign(
            { sub: user.id, email: user.email, role: user.role },
            process.env.JWT_SECRET!,
            { expiresIn: '24h' }
        );

        log?.info({ userId: user.id, email: user.email }, 'User signed up successfully');
        return res.status(201).json({
            user: { id: user.id, email: user.email, name: user.name, role: user.role, created_at: user.created_at },
            token
        });

    } catch (err) {
        log?.error({ err }, 'Error during signup: unexpected error');
        return next(err);
    }
}
