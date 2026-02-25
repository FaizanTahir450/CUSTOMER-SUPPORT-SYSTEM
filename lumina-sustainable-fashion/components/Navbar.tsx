
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { NAV_LINKS } from '../constants';
import { useAuth } from '../context/AuthContext';

const Navbar: React.FC = () => {
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <nav className="bg-white/80 backdrop-blur-md sticky top-0 z-50 border-b border-slate-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex-shrink-0 flex items-center gap-8">
            <Link to="/" className="text-2xl font-bold tracking-tighter text-slate-900">LUMINA</Link>
            <div className="hidden md:flex space-x-6">
              {NAV_LINKS.map((link) => (
                <Link
                  key={link.name}
                  to={link.path}
                  className={`text-sm font-medium transition-colors ${
                    location.pathname === link.path ? 'text-indigo-600' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {link.name}
                </Link>
              ))}
              {user?.role === 'admin' && (
                <Link
                  to="/admin"
                  className={`text-sm font-semibold transition-colors ${
                    location.pathname === '/admin' ? 'text-indigo-600' : 'text-indigo-500 hover:text-indigo-700'
                  }`}
                >
                  Admin Panel
                </Link>
              )}
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <Link 
              to="/support" 
              className="px-4 py-2 text-slate-600 text-sm font-medium hover:text-slate-900 transition-all flex items-center gap-2"
            >
              Support
            </Link>
            
            {isAuthenticated ? (
              <div className="flex items-center gap-4">
                <span className="text-xs text-slate-500 hidden sm:inline">Hi, {user?.name}</span>
                <button 
                  onClick={logout}
                  className="px-4 py-2 border border-slate-200 text-slate-700 text-sm font-medium rounded-full hover:bg-slate-50 transition-all"
                >
                  Logout
                </button>
              </div>
            ) : (
              <Link 
                to="/login" 
                className="px-5 py-2 bg-slate-900 text-white text-sm font-medium rounded-full hover:bg-slate-800 transition-all shadow-sm"
              >
                Sign In
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
