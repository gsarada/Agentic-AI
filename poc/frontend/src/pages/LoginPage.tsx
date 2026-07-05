import { type FormEvent, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api, setToken } from '../api';

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    try {
      const { access_token } = await api.login({ email, password });
      setToken(access_token);
      navigate('/profile');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    }
  }

  return (
    <div className="mx-auto max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <h1 className="mb-4 text-2xl font-semibold">Login</h1>
      <form onSubmit={onSubmit} className="space-y-4">
        <input className="input" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input
          className="input"
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        {error && <p className="text-sm text-rose-400">{error}</p>}
        <button className="btn-primary w-full">Sign in</button>
      </form>
      <p className="mt-4 text-sm text-slate-400">
        No account? <Link className="text-violet-300" to="/register">Register</Link>
      </p>
    </div>
  );
}
