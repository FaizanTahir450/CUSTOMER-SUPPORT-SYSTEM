import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { resetPassword } from '../services/authservice';

const ResetPassword: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  
  const token = searchParams.get('token');

  const validatePassword = (pwd: string): string[] => {
    const errors: string[] = [];
    if (pwd.length < 10) {
      errors.push('Password must be at least 10 characters long');
    }
    if (!/[0-9]/.test(pwd)) {
      errors.push('Password must contain at least one number');
    }
    if (!/[^A-Za-z0-9]/.test(pwd)) {
      errors.push('Password must contain at least one special character');
    }
    return errors;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validate token
    if (!token) {
      setError('Invalid or missing reset token. Please use the link from the email.');
      return;
    }

    // Validate passwords match
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Validate password strength
    const passwordErrors = validatePassword(password);
    if (passwordErrors.length > 0) {
      setError(passwordErrors.join(', '));
      return;
    }

    setLoading(true);

    try {
      await resetPassword({ token, newPassword: password });
      setSuccess(true);
    } catch (err: any) {
      setError(err.message || 'Failed to reset password. Please try again or request a new reset link.');
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="min-h-[calc(100vh-64px)] flex items-center justify-center p-8 bg-white">
        <div className="max-w-md w-full">
          <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
            <h2 className="text-xl font-semibold text-red-900 mb-2">Invalid Reset Link</h2>
            <p className="text-red-700 mb-6">
              The password reset link is missing or invalid. Please request a new one.
            </p>
            <button 
              onClick={() => navigate('/forgot-password')}
              className="w-full py-3 bg-slate-900 text-white rounded-xl font-bold hover:bg-slate-800 transition-all"
            >
              Request New Link
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-64px)] flex">
      {/* Left side: Image */}
      <div className="hidden lg:block w-1/2 relative">
        <img 
          src="https://images.unsplash.com/photo-1490481651871-ab68de25d43d?q=80&w=2070&auto=format&fit=crop" 
          alt="Fashion Background" 
          className="absolute inset-0 w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-indigo-900/20 backdrop-blur-[2px]" />
        <div className="absolute bottom-12 left-12 text-white max-w-md">
          <h2 className="text-4xl font-bold mb-4 italic tracking-tight">"Style is a way to say who you are without having to speak."</h2>
          <p className="text-lg opacity-80">— Rachel Zoe</p>
        </div>
      </div>

      {/* Right side: Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-white">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center lg:text-left">
            <h1 className="text-3xl font-bold text-slate-900">Create New Password</h1>
            <p className="mt-2 text-slate-500">
              Enter a strong password to secure your account.
            </p>
          </div>

          {!success ? (
            <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
              {error && (
                <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg border border-red-100">
                  {error}
                </div>
              )}

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">New Password</label>
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-600 outline-none transition-all"
                  />
                  <p className="mt-2 text-xs text-slate-500">
                    Password must be at least 10 characters with at least one number and one special character.
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Confirm Password</label>
                  <input
                    type="password"
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-600 outline-none transition-all"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading || !password}
                className="w-full py-4 bg-slate-900 text-white rounded-xl font-bold hover:bg-slate-800 transition-all shadow-lg shadow-slate-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Resetting...' : 'Reset Password'}
              </button>
            </form>
          ) : (
            <div className="mt-8 p-6 bg-green-50 border border-green-200 rounded-lg">
              <div className="text-center">
                <div className="text-4xl mb-4">✓</div>
                <h2 className="text-xl font-semibold text-green-900 mb-2">Password Reset Successfully</h2>
                <p className="text-green-700 mb-6">
                  Your password has been changed successfully. You can now log in with your new password.
                </p>
              </div>
            </div>
          )}

          {success && (
            <button 
              onClick={() => navigate('/login')}
              className="w-full py-3 bg-slate-900 text-white rounded-xl font-bold hover:bg-slate-800 transition-all"
            >
              Back to Login
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResetPassword;
