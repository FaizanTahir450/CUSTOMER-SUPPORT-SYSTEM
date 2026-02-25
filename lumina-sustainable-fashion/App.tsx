
import React from 'react';
import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Shop from './pages/Shop';
import Support from './pages/Support';
import Login from './pages/Login';
import Admin from './pages/Admin';
import { AuthProvider } from './context/AuthContext';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen flex flex-col bg-white">
          <Navbar />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/shop" element={<RouteWrapper><Shop /></RouteWrapper>} />
              <Route path="/support" element={<Support />} />
              <Route path="/login" element={<Login />} />
              <Route path="/admin" element={<Admin />} />
            </Routes>
          </main>
          
          <footer className="bg-white border-t border-slate-100 py-12 mt-auto">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-8">
              <div className="text-2xl font-bold tracking-tighter text-slate-900">LUMINA</div>
              <div className="flex gap-8 text-sm font-medium text-slate-500">
                <a href="#" className="hover:text-slate-900 transition-colors">Instagram</a>
                <a href="#" className="hover:text-slate-900 transition-colors">Privacy Policy</a>
                <a href="#" className="hover:text-slate-900 transition-colors">Terms of Service</a>
                <a href="#" className="hover:text-slate-900 transition-colors">Sustainability Report</a>
              </div>
              <p className="text-xs text-slate-400">© 2024 LUMINA Retail. All rights reserved.</p>
            </div>
          </footer>
        </div>
      </Router>
    </AuthProvider>
  );
};

// Simple wrapper for animation or standard layout if needed
const RouteWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="animate-in fade-in duration-500">
    {children}
  </div>
);

export default App;
