import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';
import { 
  Loader2, UserPlus, LogIn, Sparkles, QrCode, Zap, 
  ShieldCheck, ArrowRight, Store, CheckCircle2 
} from 'lucide-react';

const Login: React.FC = () => {
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const navigate = useNavigate();
  const { login } = useAuth();

  const fillDemoAccount = () => {
    setEmail('test@scango.com');
    setPassword('password123');
    setError(null);
    setSuccessMsg(null);
    setIsRegisterMode(false);
  };

  const handleAuth = async () => {
    if (!email || !password) {
      setError("Please enter both email and password.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccessMsg(null);

    try {
      if (isRegisterMode) {
        // Register user under default merchant 1
        await api.post('/auth/register', {
          email,
          password,
          store_id: 1,
          is_merchant: false
        });

        setSuccessMsg("Account created successfully! Logging you in...");
        setIsRegisterMode(false);
      }

      // Login request
      const params = new URLSearchParams();
      params.append('username', email);
      params.append('password', password);

      const response = await api.post('/auth/login', params.toString(), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      const token = response.data.access_token;
      
      // Decode JWT payload safely
      let payloadDecoded: any = {};
      try {
        const parts = token.split('.');
        const base64Url = parts[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        payloadDecoded = JSON.parse(window.atob(base64));
      } catch (e) {
        console.warn("JWT parse fallback:", e);
        payloadDecoded = { sub: email, user_id: 1, merchant_id: 1 };
      }

      const userData = {
        email: payloadDecoded.sub || email,
        user_id: payloadDecoded.user_id || 1,
        merchant_id: payloadDecoded.merchant_id || 1,
      };

      login(userData, token);
      navigate('/scan');

    } catch (err: any) {
      if (err.response && err.response.data && err.response.data.detail) {
        const detail = err.response.data.detail;
        if (typeof detail === 'string') {
          setError(detail);
        } else {
          setError("Invalid credentials or registration failed.");
        }
      } else if (err.response && err.response.status === 401) {
        setError("Invalid email or password. Use demo account or create a new account.");
      } else {
        setError("Unable to connect to backend server. Make sure port 8000 is running.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleAuth();
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 sm:p-6 lg:p-8 relative overflow-hidden">
      
      {/* Ambient Background Radial Glows */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#028090]/20 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-emerald-500/15 rounded-full blur-3xl pointer-events-none"></div>

      <div className="w-full max-w-5xl glass-card rounded-3xl overflow-hidden shadow-2xl border border-white/10 grid grid-cols-1 lg:grid-cols-12 relative z-10">
        
        {/* Left Side: Brand Showcase & Value Proposition (Lg Screens) */}
        <div className="lg:col-span-5 p-8 lg:p-12 bg-gradient-to-br from-slate-900/90 to-slate-950/90 border-b lg:border-b-0 lg:border-r border-white/10 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-3 mb-8">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-[#028090] to-[#00a896] flex items-center justify-center text-2xl text-white shadow-xl shadow-[#028090]/30">
                🛒
              </div>
              <div>
                <h1 className="text-2xl font-black text-white tracking-tight">Scan & Go</h1>
                <p className="text-xs text-[#00f5d4] font-semibold">Queue-Free Retail Platform</p>
              </div>
            </div>

            <h2 className="text-2xl lg:text-3xl font-extrabold text-white leading-tight mb-4">
              The Store Register directly in your Pocket.
            </h2>
            <p className="text-sm text-slate-400 leading-relaxed mb-8">
              Scan product barcodes with your camera, manage your cart, and checkout instantly—bypassing long cash register queues completely.
            </p>

            {/* Feature Bullet Points */}
            <div className="space-y-4">
              <div className="flex items-start gap-3 text-xs text-slate-300">
                <div className="p-1.5 rounded-lg bg-[#028090]/20 text-[#00f5d4] mt-0.5">
                  <Zap size={16} />
                </div>
                <div>
                  <span className="font-bold text-white block">Instant Camera Scanning</span>
                  Real-time browser-based barcode decoding with zero app install required.
                </div>
              </div>

              <div className="flex items-start gap-3 text-xs text-slate-300">
                <div className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400 mt-0.5">
                  <ShieldCheck size={16} />
                </div>
                <div>
                  <span className="font-bold text-white block">Frictionless Mobile Checkout</span>
                  Deducts inventory stock dynamically and finalizes purchases.
                </div>
              </div>

              <div className="flex items-start gap-3 text-xs text-slate-300">
                <div className="p-1.5 rounded-lg bg-purple-500/20 text-purple-400 mt-0.5">
                  <QrCode size={16} />
                </div>
                <div>
                  <span className="font-bold text-white block">AI Demand Forecasting</span>
                  Machine Learning models predicting stock demand for merchants.
                </div>
              </div>
            </div>
          </div>

          {/* Footer Badge */}
          <div className="mt-8 pt-6 border-t border-white/10 flex items-center justify-between text-xs text-slate-400">
            <span className="flex items-center gap-1.5">
              <Store size={14} className="text-[#028090]" /> Demo Store #01
            </span>
            <span className="text-emerald-400 font-bold flex items-center gap-1">
              <CheckCircle2 size={12} /> System Online
            </span>
          </div>
        </div>

        {/* Right Side: Auth Form */}
        <div className="lg:col-span-7 p-8 lg:p-12 flex flex-col justify-center">
          
          {/* Tab Switcher */}
          <div className="flex rounded-2xl bg-slate-900/80 p-1.5 border border-white/10 mb-8">
            <button
              onClick={() => { setIsRegisterMode(false); setError(null); }}
              className={`flex-1 py-2.5 rounded-xl text-xs font-extrabold transition-all flex items-center justify-center gap-2 ${
                !isRegisterMode
                  ? 'bg-[#028090] text-white shadow-lg shadow-[#028090]/25'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <LogIn size={15} />
              Sign In
            </button>
            <button
              onClick={() => { setIsRegisterMode(true); setError(null); }}
              className={`flex-1 py-2.5 rounded-xl text-xs font-extrabold transition-all flex items-center justify-center gap-2 ${
                isRegisterMode
                  ? 'bg-[#028090] text-white shadow-lg shadow-[#028090]/25'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <UserPlus size={15} />
              Create Account
            </button>
          </div>

          {/* One-Click Demo Button */}
          <button
            type="button"
            onClick={fillDemoAccount}
            className="w-full mb-6 p-3 rounded-2xl bg-gradient-to-r from-amber-500/15 to-orange-500/15 border border-amber-500/30 hover:border-amber-500/50 text-amber-300 text-xs font-extrabold flex items-center justify-center gap-2.5 active:scale-[0.99] transition-all group"
          >
            <Sparkles size={16} className="text-amber-400 group-hover:rotate-12 transition-transform" />
            <span>Click to Auto-Fill Pre-configured Demo Credentials</span>
            <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
          </button>

          {/* Feedback Alerts */}
          {error && (
            <div className="mb-6 p-4 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-semibold text-center">
              {error}
            </div>
          )}

          {successMsg && (
            <div className="mb-6 p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold text-center">
              {successMsg}
            </div>
          )}

          {/* Inputs Form */}
          <div className="space-y-5">
            <div>
              <label className="block text-xs font-bold text-slate-300 mb-2 uppercase tracking-wider">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onKeyDown={handleKeyDown}
                className="w-full px-4 py-3.5 rounded-2xl bg-slate-900/90 border border-slate-700/80 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-[#028090] focus:ring-2 focus:ring-[#028090]/20 transition-all"
                placeholder="test@scango.com"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-300 mb-2 uppercase tracking-wider">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyDown={handleKeyDown}
                className="w-full px-4 py-3.5 rounded-2xl bg-slate-900/90 border border-slate-700/80 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-[#028090] focus:ring-2 focus:ring-[#028090]/20 transition-all"
                placeholder="••••••••"
              />
            </div>

            <button
              onClick={handleAuth}
              disabled={isLoading}
              className="w-full py-4 rounded-2xl bg-gradient-to-r from-[#028090] to-[#00a896] hover:from-[#026c7a] hover:to-[#008f80] text-white text-sm font-extrabold shadow-xl shadow-[#028090]/25 flex items-center justify-center gap-2 active:scale-[0.98] disabled:opacity-60 transition-all"
            >
              {isLoading ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  <span>{isRegisterMode ? "Creating Account..." : "Authenticating..."}</span>
                </>
              ) : isRegisterMode ? (
                <>
                  <UserPlus size={18} />
                  <span>Create Free Account</span>
                </>
              ) : (
                <>
                  <LogIn size={18} />
                  <span>Sign In to App</span>
                </>
              )}
            </button>
          </div>

        </div>

      </div>
    </div>
  );
};

export default Login;
