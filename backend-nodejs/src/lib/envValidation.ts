import { logger } from './logger';

/**
 * Validate required environment variables at startup
 */
export function validateEnvironment() {
  const requiredVars = [
    'MYSQL_HOST',
    'MYSQL_USER',
    'MYSQL_DATABASE',
    'JWT_SECRET',
    'PORT'
  ];

  const emailVars = [
    'Email_SMTP_HOST',
    'Email_SMTP_USER',
    'Email_SMTP_PASSWORD',
    'Email_SMTP_FROM',
    'FRONTEND_BASE_URL'
  ];

  const missingVars: string[] = [];

  // Check required vars
  requiredVars.forEach(varName => {
    if (!process.env[varName]) {
      missingVars.push(varName);
    }
  });

  // Check email vars (warn but don't fail)
  const missingEmailVars: string[] = [];
  emailVars.forEach(varName => {
    if (!process.env[varName]) {
      missingEmailVars.push(varName);
    }
  });

  if (missingVars.length > 0) {
    logger.error({ missingVars }, 'Missing required environment variables');
    throw new Error(`Missing required environment variables: ${missingVars.join(', ')}`);
  }

  if (missingEmailVars.length > 0) {
    logger.warn({ missingEmailVars }, 'Missing email configuration variables - password reset may not work');
  }

  logger.info('Environment validation passed');
}
