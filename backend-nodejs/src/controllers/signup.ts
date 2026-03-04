import { Request, Response, NextFunction } from 'express'
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { z } from 'zod';
import type { RowDataPacket } from 'mysql2';
import { pool } from '../lib/db';

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
    const log = (req as any).log;
    try {
        const parsed = signupSchema.safeParse(req.body);
        if (!parsed.success) {
            return res.status(400).json({
                error: { code: "validation error", message: parsed.error.issues[0]?.message || 'Invalid input' }
            });
        }
        const { email, password, name } = parsed.data;
        const [existingUser] = await pool.execute<RowDataPacket[]>(
            `select id from users where email = ?`, [email]);
        if (existingUser.length > 0) {
            return res.status(409).json({
                error: { code: "Email exists", message: "An account with this email already exists" }
            })
        };
        const passwordHash = await bcrypt.hash(password,12);
        await pool.execute(
            `INSERT INTO users (id,email,password_hash,name)
            values (UUID(),?,?,?)`,
            [email, passwordHash, name || null]
        )
        const [users] = await pool.execute<RowDataPacket[]>(
            `select id,email,name,created_at from users where email = ?`, [email]);
        const user = users[0];
        if(!user){
            throw new Error('User insert failed');
        }
        const token = jwt.sign(
            {sub:user.id,email:user.email},
            process.env.JWT_SECRET || 'default_secret',
            {expiresIn:'24h'}
        );

        log?.info({userId:user.id,email:user.email},'User signed up successfully');
        return res.status(201).json({
            user: {id:user.id,email:user.email,name:user.name,created_at:user.created_at},
            token
        });

        
    }catch(err){
        log?.error(err, 'Error during signup');
        return next(err);
    }
}
