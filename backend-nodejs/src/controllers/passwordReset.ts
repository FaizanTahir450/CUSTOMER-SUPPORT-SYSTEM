import { Request, Response, NextFunction } from 'express';
import { z } from 'zod';
import { supabase } from '../lib/db';
import { v4 as uuidv4 } from 'uuid';
import bcrypt from 'bcryptjs';
import nodemailer from 'nodemailer';
import crypto from 'crypto';
import { logger } from '../lib/logger';

const emailTransporter = nodemailer.createTransport({
    host: process.env.Email_SMTP_HOST,
    port: 587,
    secure: false,
    auth: {
        user: process.env.Email_SMTP_USER,
        pass: process.env.Email_SMTP_PASSWORD
    },
    tls: {
        rejectUnauthorized: false
    }
});

const forgetPasswordSchema = z.object({
    email: z.string().email('invalid email address').trim().toLowerCase()
});

const resetPasswordSchema = z.object({
    token: z.string().min(1, 'Token is required'),
    newPassword: z.string().min(10, 'Password must be at least 10 characters long')
        .regex(/[0-9]/, 'Password must contain at least one number')
        .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character')
});

function hashToken(token: string): string {
    return crypto.createHash('sha256').update(token).digest('hex');
}

export async function requestPasswordResetHandler(req: Request, res: Response, next: NextFunction) {
    const log = (req as any).log || logger;
    try {
        log?.debug({ email: req.body.email }, 'Password reset request attempt');
        const parsed = forgetPasswordSchema.safeParse(req.body);
        if (!parsed.success) {
            log?.warn({ errors: parsed.error.issues }, 'Password reset validation failed');
            return res.status(400).json(
                { error: { code: 'validation error', message: parsed.error.issues[0]?.message || 'invalid input' } }
            );
        }
        const { email } = parsed.data;
        log?.debug({ email }, 'Checking if user exists');
        
        // CHECK IF USER EXISTS
        const { data: user, error: selectError } = await supabase
            .from('users')
            .select('id')
            .eq('email', email)
            .maybeSingle();
        
        if (selectError && selectError.code !== 'PGRST116') {
            throw selectError;
        }

        if (!user) {
            log?.warn({ email }, 'Password reset requested for non-existent user');
            return res.status(200).json({ message: 'If an account with that email exists, a password reset link has been sent' });
        }
        
        const userId = user.id;
        log?.debug({ email }, 'Generating reset token');
        const resetToken = crypto.randomBytes(32).toString('hex');
        const hashedToken = hashToken(resetToken);

        try {
            log?.debug({ userId, email }, 'Storing reset token in database');
            const expiresAt = new Date();
            expiresAt.setHours(expiresAt.getHours() + 1);
            
            const { error: insertError } = await supabase
                .from('password_reset_tokens')
                .insert([{
                    id: uuidv4(),
                    user_id: userId,
                    token: hashedToken,
                    expires_at: expiresAt.toISOString()
                }]);
            
            if (insertError) throw insertError;
            log?.debug({ userId }, 'Reset token stored successfully');

        } catch (err) {
            log?.error({ err, email }, 'Failed to store reset token');
            return res.status(500).json({ error: { code: 'db_error', message: 'Failed to process password reset. Please try again later.' } });
        }

        try {
            log?.debug({ email }, 'Sending password reset email');
            const resetlink = `${process.env.FRONTEND_BASE_URL}reset-password?token=${resetToken}`;
            await emailTransporter.sendMail({
                from: process.env.Email_SMTP_FROM,
                to: email,
                subject: 'Password Reset Request - LUMINA',
                text: `You requested a password reset. Click the link to reset your password: ${resetlink}\n\nThis link will expire in 1 hour.`,
                html: `
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
      body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }
      .container { max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9fafb; }
      .email-wrapper { background-color: #ffffff; border-radius: 8px; shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden; }
      .header { background: linear-gradient(135deg, #1f2937 0%, #111827 100%); color: #ffffff; padding: 40px 20px; text-align: center; }
      .logo { font-size: 28px; font-weight: bold; margin-bottom: 10px; letter-spacing: 2px; }
      .content { padding: 40px 20px; }
      .greeting { font-size: 18px; font-weight: 600; color: #1f2937; margin-bottom: 20px; }
      .message { color: #666; margin-bottom: 10px; font-size: 14px; }
      .button-container { text-align: center; margin: 30px 0; }
      .reset-button { display: inline-block; background-color: #4f46e5; color: #ffffff; padding: 12px 32px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 16px; transition: background-color 0.3s; }
      .reset-button:hover { background-color: #4338ca; }
      .link-text { color: #666; font-size: 12px; margin-top: 15px; word-break: break-all; }
      .link-text a { color: #4f46e5; text-decoration: none; }
      .warning { background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 12px; margin: 20px 0; border-radius: 4px; font-size: 14px; color: #92400e; }
      .footer { background-color: #f3f4f6; padding: 20px; text-align: center; border-top: 1px solid #e5e7eb; font-size: 12px; color: #666; }
      .footer-text { margin: 5px 0; }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="email-wrapper">
        <div class="header">
          <div class="logo">LUMINA</div>
          <p style="margin: 0; font-size: 14px; opacity: 0.9;">Sustainable Fashion Platform</p>
        </div>
        <div class="content">
          <div class="greeting">Hello,</div>
          <p class="message">We received a request to reset your password for your LUMINA account. If you didn't make this request, you can safely ignore this email.</p>
          <p class="message">To reset your password, click the button below:</p>
          <div class="button-container">
            <a href="${resetlink}" class="reset-button">Reset Your Password</a>
          </div>
          <p class="link-text">
            Or copy and paste this link in your browser:<br>
            <a href="${resetlink}">${resetlink}</a>
          </p>
          <div class="warning">
            <strong>⏱️ This link will expire in 1 hour.</strong> Please reset your password as soon as possible.
          </div>
          <p class="message" style="margin-top: 30px;">
            If you have any questions or need further assistance, please don't hesitate to contact our support team.
          </p>
        </div>
        <div class="footer">
          <p class="footer-text">© 2026 LUMINA. All rights reserved.</p>
          <p class="footer-text">Security is our priority. Never share your password reset link with anyone.</p>
          <p class="footer-text"><a href="${process.env.FRONTEND_BASE_URL}" style="color: #4f46e5; text-decoration: none;">Visit LUMINA</a></p>
        </div>
      </div>
    </div>
  </body>
</html>
                `
            });
            log?.info({ email }, 'Password reset email sent successfully');
            return res.status(200).json({ message: 'If an account with that email exists, a password reset link has been sent' });
        } catch (err) {
            log?.error({ err, email }, 'Failed to send password reset email');
            return res.status(500).json({ error: { code: 'email_error', message: 'Failed to send password reset email. Please try again later.' } });
        }

    } catch (err) {
        log?.error({ err }, 'Unexpected error in password reset request');
        return next(err);
    }
}

export async function resetPasswordHandler(req: Request, res: Response, next: NextFunction) {
    const log = (req as any).log || logger;
    try {
        log?.debug({ token: req.body.token?.substring(0, 10) + '...' }, 'Password reset attempt');
        const parsed = resetPasswordSchema.safeParse(req.body);
        if (!parsed.success) {
            log?.warn({ errors: parsed.error.issues }, 'Password reset validation failed');
            return res.status(400).json({ error: { code: 'validation error', message: parsed.error.issues[0]?.message || 'invalid input' } });
        }
        const { token, newPassword } = parsed.data;
        
        log?.debug('Validating reset token');
        const hashedToken = hashToken(token);
        
        // GET RESET TOKEN
        const { data: resetTokenData, error: selectError } = await supabase
            .from('password_reset_tokens')
            .select('user_id')
            .eq('token', hashedToken)
            .gt('expires_at', new Date().toISOString())
            .is('used_at', null)
            .maybeSingle();
        
        if (selectError && selectError.code !== 'PGRST116') {
            throw selectError;
        }
        
        if (!resetTokenData) {
            log?.warn('Password reset failed: invalid or expired token');
            return res.status(400).json({ error: { code: 'invalid_token', message: 'Invalid or expired token' } });
        }
        
        const userId = resetTokenData.user_id;
        log?.debug({ userId }, 'Hashing new password');
        const passwordHash = await bcrypt.hash(newPassword, 10);
        
        log?.debug({ userId }, 'Updating user password');
        const { error: updateError } = await supabase
            .from('users')
            .update({ password_hash: passwordHash })
            .eq('id', userId);
        
        if (updateError) throw updateError;
        
        log?.debug({ userId }, 'Marking token as used');
        const { error: markError } = await supabase
            .from('password_reset_tokens')
            .update({ used_at: new Date().toISOString() })
            .eq('token', hashedToken);
        
        if (markError) throw markError;
        
        log?.info({ userId }, 'Password reset successfully completed');
        return res.status(200).json({ message: 'Password has been reset successfully' });
    } catch (err) {
        log?.error({ err }, 'Unexpected error during password reset');
        return next(err);
    }
}
