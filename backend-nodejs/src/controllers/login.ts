import { Request, Response, NextFunction } from 'express';
import { z } from 'zod';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import type { RowDataPacket } from 'mysql2';
import { pool } from '../lib/db';

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
    const log = (req as any).log;
    try {
        const parsed = loginschema.safeParse(req.body);
        if (!parsed.success) {
            return res.status(400).json({
                error: { code: "validation error", message: parsed.error.issues[0]?.message || 'invalid input' }
            });
        }
        const { email, password } = parsed.data;
        const [users] = await pool.execute<RowDataPacket[]>(
            `select id,email,password_hash,name,created_at from users where email = ?`, [email]
        );
        const user = users[0];
        if (!user) {
            log?.warn({ email }, 'Login failed invalid password');
            return res.status(401).json({
                error: { code: "invalid credentials", message: "Invalid email or password    " }
            })
        }
        const match = await bcrypt.compare(password,user.password_hash);
        if(!match){
            return res.status(401).json({error:{code:"invalid credentials",message:"Invalid email or password"}})
        }

        const token = jwt.sign(
            { sub: user.id, email: user.email },
            process.env.JWT_SECRET || 'default_secret',
            { expiresIn: '7d' }

        );
        log?.info({ userId: user.id, email: user.email }, 'Login successful');
        return res.status(200).json({
            user: { id: user.id, email: user.email, name: user.name, createdAt: user.created_at },
            token
        });

    }
    catch (err) {
        log?.error({ err }, 'Login error');
        return next(err);
    }
}

