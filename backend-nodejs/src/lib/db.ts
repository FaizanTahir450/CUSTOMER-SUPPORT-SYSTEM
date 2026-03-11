import { createClient } from '@supabase/supabase-js';
import { logger } from './logger';


const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY;

if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
    throw new Error('Missing SUPABASE_URL or SUPABASE_ANON_KEY environment variables');
}

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

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
