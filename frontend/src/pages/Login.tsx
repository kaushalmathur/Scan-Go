import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';
import { Loader2 } from 'lucide-react';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();
  const { login } = useAuth();

  const handleLogin = async () => {
    if (!email || !password) {
      setError("Please enter both email and password.");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // FastAPI OAuth2 requires x-www-form-urlencoded
      const params = new URLSearchParams();
      params.append('username', email);
      params.append('password', password);

      const response = await api.post('/auth/login', params.toString(), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      const token = response.data.access_token;
      
      // Decode JWT payload
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      
      const payloadDecoded = JSON.parse(jsonPayload);

      // Create a user object from token claims
      const userData = {
        email: payloadDecoded.sub,
        user_id: payloadDecoded.user_id,
        merchant_id: payloadDecoded.merchant_id,
      };

      login(userData, token);
      
      // Redirect to scanner
      navigate('/scan');

    } catch (err: any) {
      if (err.response && err.response.status === 401) {
        setError("Invalid email or password.");
      } else {
        setError("An error occurred during login. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleLogin();
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-900 px-4 text-white">
      <div className="w-full max-w-md space-y-8 rounded-2xl bg-slate-800 p-8 shadow-xl border border-slate-700">
        
        <div className="text-center">
          <h2 className="text-3xl font-extrabold tracking-tight">Scan & Go</h2>
          <p className="mt-2 text-sm text-slate-400">Sign in to start scanning</p>
        </div>

        {error && (
          <div className="rounded-lg bg-red-500/10 p-3 text-sm text-red-500 border border-red-500/20 text-center font-medium">
            {error}
          </div>
        )}

        <div className="space-y-5">
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-300">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onKeyDown={handleKeyDown}
              className="block w-full rounded-lg border border-slate-600 bg-slate-700 p-3 text-white placeholder-slate-400 focus:border-[#028090] focus:ring-1 focus:ring-[#028090] focus:outline-none transition-colors"
              placeholder="shopper@example.com"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-300">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={handleKeyDown}
              className="block w-full rounded-lg border border-slate-600 bg-slate-700 p-3 text-white placeholder-slate-400 focus:border-[#028090] focus:ring-1 focus:ring-[#028090] focus:outline-none transition-colors"
              placeholder="••••••••"
            />
          </div>

          <button
            onClick={handleLogin}
            disabled={isLoading}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-[#028090] p-3 text-sm font-bold text-white shadow-lg hover:bg-[#026c7a] focus:outline-none active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed transition-all"
          >
            {isLoading ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                Authenticating...
              </>
            ) : (
              'Log In'
            )}
          </button>
        </div>

      </div>
    </div>
  );
};

export default Login;
