import React from 'react';

const Login: React.FC = () => {
  return (
    <div className="flex h-screen items-center justify-center bg-gray-50">
      <div className="w-full max-w-md space-y-8 rounded-lg bg-white p-6 shadow-md">
        <h2 className="text-center text-3xl font-bold text-gray-900">Sign in to Scan & Go</h2>
        <form className="space-y-4">
          <input className="block w-full rounded border p-2" type="email" placeholder="Email" />
          <input className="block w-full rounded border p-2" type="password" placeholder="Password" />
          <button className="w-full rounded bg-primary-600 p-2 text-white hover:bg-primary-700">Login</button>
        </form>
      </div>
    </div>
  );
};

export default Login;
