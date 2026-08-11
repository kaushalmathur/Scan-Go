import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';
import { 
  Menu, X, LogOut, ShoppingCart, Activity, Tag, QrCode, 
  Store, User as UserIcon, Sparkles 
} from 'lucide-react';

const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [cartCount, setCartCount] = useState<number>(0);

  const fetchCartCount = async () => {
    if (!user?.user_id || location.pathname === '/login') return;
    try {
      const res = await api.get(`/cart/${user.user_id}`);
      const items = res.data?.items || [];
      const totalQty = items.reduce((acc: number, item: { quantity: number }) => acc + (item.quantity || 1), 0);
      setCartCount(totalQty);
    } catch {
      // Ignore 404 or missing cart
    }
  };

  useEffect(() => {
    fetchCartCount();
    const interval = setInterval(fetchCartCount, 5000);
    return () => clearInterval(interval);
  }, [user, location.pathname]);

  // Hide the Navbar on login page AFTER all hooks
  if (location.pathname === '/login') return null;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const closeMenu = () => {
    setIsMobileMenuOpen(false);
  };

  const navLinks = [
    { name: 'Scan & Go', path: '/scan', icon: <QrCode size={18} /> },
    { name: 'Cart', path: '/cart', icon: <ShoppingCart size={18} />, badge: cartCount },
    { name: 'Merchant Dashboard', path: '/dashboard', icon: <Activity size={18} /> },
    { name: 'Store Products', path: '/products', icon: <Tag size={18} /> },
  ];

  return (
    <nav className="glass-nav sticky top-0 z-50 transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Store Location Badge - Left */}
          <div className="flex items-center gap-4">
            <Link to="/scan" onClick={closeMenu} className="flex items-center gap-2.5 group">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#028090] to-[#00a896] flex items-center justify-center text-white shadow-lg shadow-[#028090]/20 group-hover:scale-105 transition-transform">
                <span className="text-xl">🛒</span>
              </div>
              <div className="flex flex-col">
                <span className="text-white text-lg font-black tracking-tight flex items-center gap-1.5">
                  Scan & Go
                  <span className="text-[10px] uppercase font-extrabold tracking-wider bg-[#028090]/20 text-[#00f5d4] px-2 py-0.5 rounded-full border border-[#028090]/30">
                    PRO
                  </span>
                </span>
                <span className="text-[11px] text-slate-400 font-medium flex items-center gap-1">
                  <Store size={12} className="text-[#028090]" /> Demo Store #01
                </span>
              </div>
            </Link>
          </div>

          {/* Desktop Navigation Links - Middle/Right */}
          <div className="hidden md:flex items-center space-x-2">
            {navLinks.map((link) => {
              const isActive = location.pathname === link.path;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`relative flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all duration-200 ${
                    isActive
                      ? 'bg-[#028090] text-white shadow-lg shadow-[#028090]/25'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                  }`}
                >
                  {link.icon}
                  {link.name}
                  {link.badge !== undefined && link.badge > 0 && (
                    <span className={`ml-1 text-[10px] font-extrabold px-1.5 py-0.5 rounded-full ${
                      isActive ? 'bg-white text-[#028090]' : 'bg-[#028090] text-white'
                    }`}>
                      {link.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </div>

          {/* User Profile Pill & Logout - Right */}
          <div className="hidden md:flex items-center gap-3 border-l border-slate-800 pl-4">
            <div className="flex items-center gap-2 bg-slate-800/80 px-3 py-1.5 rounded-xl border border-slate-700/60 text-xs text-slate-300">
              <div className="w-6 h-6 rounded-full bg-[#028090]/30 text-[#00f5d4] flex items-center justify-center font-bold text-[11px]">
                <UserIcon size={13} />
              </div>
              <div className="flex flex-col">
                <span className="font-semibold text-slate-200 truncate max-w-[120px]">
                  {user?.email || 'Shopper'}
                </span>
                <span className="text-[10px] text-emerald-400 font-bold flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> Active
                </span>
              </div>
            </div>

            <button
              onClick={handleLogout}
              className="p-2 rounded-xl text-slate-400 hover:text-red-400 hover:bg-red-500/10 border border-transparent hover:border-red-500/20 transition-all"
              title="Sign Out"
            >
              <LogOut size={18} />
            </button>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center gap-2">
            <Link
              to="/cart"
              className="relative p-2 rounded-xl bg-slate-800 text-slate-200 border border-slate-700"
            >
              <ShoppingCart size={20} />
              {cartCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-[#028090] text-white text-[10px] font-bold w-5 h-5 rounded-full flex items-center justify-center">
                  {cartCount}
                </span>
              )}
            </Link>

            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2 rounded-xl bg-slate-800 text-slate-300 hover:text-white border border-slate-700 transition-colors"
            >
              {isMobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {isMobileMenuOpen && (
        <div className="md:hidden glass-card border-t border-slate-800 px-4 pt-3 pb-6 space-y-2 animate-fadeIn">
          {navLinks.map((link) => {
            const isActive = location.pathname === link.path;
            return (
              <Link
                key={link.path}
                to={link.path}
                onClick={closeMenu}
                className={`flex items-center justify-between px-4 py-3 rounded-xl text-sm font-bold transition-all ${
                  isActive
                    ? 'bg-[#028090] text-white'
                    : 'text-slate-300 hover:bg-slate-800'
                }`}
              >
                <div className="flex items-center gap-3">
                  {link.icon}
                  {link.name}
                </div>
                {link.badge !== undefined && link.badge > 0 && (
                  <span className="bg-white text-[#028090] text-xs font-extrabold px-2 py-0.5 rounded-full">
                    {link.badge}
                  </span>
                )}
              </Link>
            );
          })}

          <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between px-2">
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <Sparkles size={14} className="text-amber-400" />
              <span className="truncate">{user?.email}</span>
            </div>
            <button
              onClick={() => {
                closeMenu();
                handleLogout();
              }}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-red-500/10 text-red-400 text-xs font-bold border border-red-500/20"
            >
              <LogOut size={14} />
              Logout
            </button>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
