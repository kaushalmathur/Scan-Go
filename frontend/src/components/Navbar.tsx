import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Menu, X, LogOut, ShoppingCart, Activity, Tag, QrCode } from 'lucide-react';

const Navbar: React.FC = () => {
  const { logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Hide the Navbar entirely on the login page
  if (location.pathname === '/login') return null;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const closeMenu = () => {
    setIsMobileMenuOpen(false);
  };

  const navLinks = [
    { name: 'Scan', path: '/scan', icon: <QrCode size={18} /> },
    { name: 'Cart', path: '/cart', icon: <ShoppingCart size={18} /> },
    { name: 'Dashboard', path: '/dashboard', icon: <Activity size={18} /> },
    { name: 'Products', path: '/products', icon: <Tag size={18} /> },
  ];

  return (
    <nav className="bg-slate-900 border-b border-slate-700 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo - Left */}
          <div className="flex-shrink-0 flex items-center">
            <Link to="/scan" onClick={closeMenu} className="flex items-center gap-2">
              <span className="text-[#028090] text-2xl font-black tracking-tighter">🛒 Scan & Go</span>
            </Link>
          </div>

          {/* Desktop Menu - Right */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-center space-x-6">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`flex items-center gap-2 text-sm font-medium transition-colors hover:text-[#028090] ${
                    location.pathname === link.path ? 'text-[#028090]' : 'text-slate-300'
                  }`}
                >
                  {link.icon}
                  {link.name}
                </Link>
              ))}
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 text-slate-300 hover:text-red-400 text-sm font-medium transition-colors ml-4 pl-4 border-l border-slate-700"
              >
                <LogOut size={18} />
                Logout
              </button>
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md justify-between text-slate-400 hover:text-white hover:bg-slate-800 focus:outline-none transition-colors"
            >
              {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Panel */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-slate-800 border-b border-slate-700 shadow-xl absolute w-full">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 flex flex-col">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                onClick={closeMenu}
                className={`flex items-center gap-3 px-3 py-4 rounded-md text-base font-medium transition-colors ${
                  location.pathname === link.path
                    ? 'bg-slate-900 text-[#028090]'
                    : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                }`}
              >
                {link.icon}
                {link.name}
              </Link>
            ))}
            <button
              onClick={() => {
                closeMenu();
                handleLogout();
              }}
              className="flex items-center gap-3 w-full text-left px-3 py-4 rounded-md text-base font-medium text-red-400 hover:bg-red-400/10 transition-colors mt-2 border-t border-slate-700"
            >
              <LogOut size={18} />
              Logout
            </button>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
