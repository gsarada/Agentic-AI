import { Link, Outlet, useNavigate } from 'react-router-dom';
import { clearToken, getToken } from '../api';

export default function Layout() {
  const navigate = useNavigate();
  const authed = !!getToken();

  function logout() {
    clearToken();
    navigate('/login');
  }

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <Link to="/" className="text-lg font-semibold text-violet-300">
            AI Personal Stylist
          </Link>
          <nav className="flex flex-wrap gap-4 text-sm text-slate-300">
            {authed ? (
              <>
                <Link to="/profile">Profile</Link>
                <Link to="/upload">Upload</Link>
                <Link to="/product">Product</Link>
                <Link to="/chat">Chat</Link>
                <Link to="/history">History</Link>
                <button onClick={logout} className="text-rose-300 hover:text-rose-200">
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login">Login</Link>
                <Link to="/register">Register</Link>
              </>
            )}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}
