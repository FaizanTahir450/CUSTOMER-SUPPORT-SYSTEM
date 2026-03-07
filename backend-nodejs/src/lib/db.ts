import { createClient } from '@supabase/supabase-js';
import { logger } from './logger';

/**
 * Supabase Client for PostgreSQL Connection
 * Replaces mysql2/promise pool for database operations
 */

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY;

if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
    throw new Error('Missing SUPABASE_URL or SUPABASE_ANON_KEY environment variables');
}

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

/**
 * Initialize database connection
 * No longer needed with Supabase, but kept for compatibility
 * Schema is already created in Supabase from migration scripts
 */
export async function ensureSchema() {
    try {
        logger.info('Verifying Supabase connection...');
        const { data, error } = await supabase.from('users').select('count', { count: 'exact' });
        
        if (error) {
            logger.error('Failed to verify Supabase connection', error);
            throw error;
        }
        
        logger.info('✅ Supabase connection verified');
        logger.info('📊 Database schema already exists in Supabase');
        return true;
    } catch (err) {
        logger.error('Schema verification failed:', err);
        throw err;
    }
}

/**
 * Helper function to extract error details from Supabase responses
 */
export function getErrorDetails(error: any) {
    if (!error) return null;
    
    return {
        code: error.code || error.status,
        message: error.message,
        details: error.details || error.hint
    };
}

/**
 * Health check for database
 */
export async function healthCheck() {
    try {
        const { error } = await supabase.from('users').select('count', { count: 'exact' });
        return !error;
    } catch {
        return false;
    }
}
