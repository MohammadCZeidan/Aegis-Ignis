import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Shield, Loader2, Sparkles, Lock } from 'lucide-react';
import logo from '../../assets/aegis-logo.png';

export function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const success = await login(email, password);
      if (success) {
        navigate('/dashboard');
      } else {
        setError('Invalid credentials. Please try again.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950 px-4 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      <div className="w-full max-w-md relative z-10">
        <div className="bg-slate-900/50 backdrop-blur-2xl rounded-3xl shadow-2xl border border-white/10 p-8 lg:p-10">
          {/* Logo and Title */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center mb-6 relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full blur-2xl opacity-40 animate-pulse"></div>
              <img src={logo} alt="Aegis Ignis" className="h-20 w-20 lg:h-24 lg:w-24 relative drop-shadow-2xl" />
            </div>
            <h1 className="text-3xl lg:text-4xl font-bold mb-2 bg-gradient-to-r from-blue-400 via-cyan-300 to-blue-400 bg-clip-text text-transparent">
              Aegis Ignis
            </h1>
            <p className="text-slate-400 text-sm lg:text-base">Smart Building Security & Fire Detection</p>
            <div className="mt-2 flex items-center justify-center gap-2 text-xs text-slate-500">
              <Lock className="h-3 w-3" />
              <span>Secure Login Portal</span>
            </div>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <Alert variant="destructive" className="bg-red-500/10 border-red-500/50 backdrop-blur-sm">
                <AlertDescription className="text-red-300">{error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="email" className="text-slate-300">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="admin@aegis-ignis.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading}
                className="h-12 bg-slate-800/50 border-slate-700 text-white placeholder:text-slate-500 focus:border-blue-500 focus:ring-blue-500/20"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-slate-300">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
                className="h-12 bg-slate-800/50 border-slate-700 text-white placeholder:text-slate-500 focus:border-blue-500 focus:ring-blue-500/20"
              />
            </div>

            <Button
              type="submit"
              className="w-full h-12 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 transition-all"
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Signing in...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-5 w-5" />
                  Sign In
                </>
              )}
            </Button>
          </form>

          {/* Demo Credentials */}
          <div className="mt-6 pt-6 border-t border-slate-700/50">
            <p className="text-xs text-slate-500 text-center mb-3 flex items-center justify-center gap-1">
              <Shield className="h-3 w-3" />
              Demo Credentials
            </p>
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 text-xs space-y-2 border border-slate-700/30">
              <div className="flex items-center justify-between text-slate-400">
                <span className="font-medium">Admin:</span>
                <code className="text-cyan-400">admin@aegis-ignis.com / admin123</code>
              </div>
              <div className="flex items-center justify-between text-slate-400">
                <span className="font-medium">User:</span>
                <code className="text-cyan-400">user@aegis-ignis.com / user123</code>
              </div>
            </div>
          </div>

          {/* Back to Landing */}
          <div className="mt-6 text-center">
            <button
              type="button"
              onClick={() => navigate('/landing')}
              className="text-sm text-slate-400 hover:text-cyan-400 transition-colors underline decoration-dotted"
            >
              ← Back to Home
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
