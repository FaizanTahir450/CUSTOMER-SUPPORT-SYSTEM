import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { forgetPassword } from '../services/authservice';

const ForgotPassword: React.FC = () => {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await forgetPassword({ email });
      setSuccess(true);
      setEmail('');
    } catch (err: any) {
      setError(err.message || 'Failed to send reset email. Please try again.');
    } finally {
      setLoading(false);
    }
  };

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
            <h1 className="text-3xl font-bold text-slate-900">Reset Your Password</h1>
            <p className="mt-2 text-slate-500">
              Enter your email address and we'll send you a link to reset your password.
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
                  <label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="your.email@example.com"
                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-600 outline-none transition-all"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-4 bg-slate-900 text-white rounded-xl font-bold hover:bg-slate-800 transition-all shadow-lg shadow-slate-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Sending...' : 'Send Reset Link'}
              </button>
            </form>
          ) : (
            <div className="mt-8 p-6 bg-green-50 border border-green-200 rounded-lg">
              <div className="text-center">
                <div className="text-4xl mb-4">✓</div>
                <h2 className="text-xl font-semibold text-green-900 mb-2">Check Your Email</h2>
                <p className="text-green-700 mb-6">
                  We've sent a password reset link to <strong>{email}</strong>. 
                  The link will expire in 1 hour.
                </p>
                <p className="text-sm text-green-600 mb-6">
                  If you don't see the email, please check your spam folder.
                </p>
              </div>
            </div>
          )}

          <div className="text-center">
            <button 
              onClick={() => navigate('/login')}
              className="text-sm text-slate-500 hover:text-indigo-600 transition-colors"
            >
              Back to Login
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
