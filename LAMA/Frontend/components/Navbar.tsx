
import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';

const NavIcon: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="p-2 rounded-full hover:bg-gray-100 cursor-pointer transition-colors">
    {children}
  </div>
);

const Navbar: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const navLinks = [
    { to: '/', text: 'Home' },
    { to: '/about', text: 'About' },
    { to: '/products', text: 'Products' },
    { to: '/contact', text: 'Contact' },
    { to: '/support', text: 'Support' },
  ];

  return (
    <header className="sticky top-0 bg-white shadow-sm z-50 animate-fade-in">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Left: Nav Links (Desktop) */}
          <div className="hidden lg:flex items-center space-x-6">
            <NavLink to="/" className="text-gray-500 hover:text-secondary transition-colors">EN</NavLink>
            <span className="text-gray-300">|</span>
            <NavLink to="/" className="text-gray-500 hover:text-secondary transition-colors">$USD</NavLink>
          </div>

          {/* Center: Logo */}
          <div className="absolute left-1/2 -translate-x-1/2 lg:relative lg:left-0 lg:translate-x-0">
            <NavLink to="/" className="text-3xl font-extrabold tracking-wider text-secondary">
              LAMA
            </NavLink>
          </div>

          {/* Right: Icons & Links */}
          <div className="flex items-center space-x-4">
            <div className="hidden lg:flex items-center space-x-6 text-lg font-medium">
              {navLinks.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  className={({ isActive }) =>
                    `relative text-gray-600 hover:text-secondary transition-colors after:content-[''] after:absolute after:left-0 after:bottom-[-2px] after:h-[2px] after:bg-primary after:transition-all after:duration-300 ${
                      isActive ? 'after:w-full' : 'after:w-0'
                    }`
                  }
                >
                  {link.text}
                </NavLink>
              ))}
            </div>
            <div className="flex items-center space-x-3">
              <NavIcon>
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
              </NavIcon>
              <NavIcon>
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
              </NavIcon>
              <div className="relative cursor-pointer">
                <NavIcon>
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path><line x1="3" y1="6" x2="21" y2="6"></line><path d="M16 10a4 4 0 0 1-8 0"></path></svg>
                </NavIcon>
                <span className="absolute top-0 right-0 flex items-center justify-center w-5 h-5 text-xs text-white bg-primary rounded-full">2</span>
              </div>
            </div>
            {/* Hamburger Menu */}
            <div className="lg:hidden">
              <button onClick={() => setIsMenuOpen(!isMenuOpen)} className="p-2 rounded-md text-gray-600 hover:text-secondary hover:bg-gray-100 focus:outline-none">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
              </button>
            </div>
          </div>
        </div>
      </div>
      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="lg:hidden animate-fade-in bg-white shadow-lg">
          <div className="flex flex-col items-center space-y-4 py-4">
            {navLinks.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                onClick={() => setIsMenuOpen(false)}
                className={({ isActive }) => `text-lg font-medium ${isActive ? 'text-primary' : 'text-gray-600'} hover:text-primary transition-colors`}
              >
                {link.text}
              </NavLink>
            ))}
          </div>
        </div>
      )}
    </header>
  );
};

export default Navbar;
