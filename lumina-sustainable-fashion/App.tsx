
import React from 'react';
import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Shop from './pages/Shop';
import Support from './pages/Support';
import Login from './pages/Login';
import Admin from './pages/Admin';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import { authToken } from './services/client';


function RequireAuth({ children }: { children: React.ReactNode }) {
  const token = authToken.get();
  if (!token)
    return <Navigate to="/login" replace />;
  return <>{children} </>;

}
const App: React.FC = () => {
  return (

      <Router>
        <div className="min-h-screen flex flex-col bg-white">
          <Navbar />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/shop" element={<RequireAuth><RouteWrapper><Shop /></RouteWrapper></RequireAuth>} />
              <Route path="/support" element={<RequireAuth><Support /></RequireAuth>} />
              <Route path="/login" element={<Login />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password" element={<ResetPassword />} />
              <Route path="/admin" element={<RequireAuth><Admin /></RequireAuth>} />
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
    
  );
};

// Simple wrapper for animation or standard layout if needed
const RouteWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="animate-in fade-in duration-500">
    {children}
  </div>
);

export default App;
