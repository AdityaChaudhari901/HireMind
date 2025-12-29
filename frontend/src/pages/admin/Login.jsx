import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Input, Button, Card, CardBody } from '../../components/common';
import { Shield, Mail, Lock } from 'lucide-react';

export default function AdminLogin() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const { login } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await login(email, password);
            navigate('/admin/dashboard');
        } catch (err) {
            setError(err.response?.data?.detail || 'Invalid credentials');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900 flex items-center justify-center p-4">
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-white/10 backdrop-blur-sm mb-4">
                        <Shield className="w-8 h-8 text-white" />
                    </div>
                    <h1 className="text-3xl font-bold text-white">Admin Portal</h1>
                    <p className="text-primary-200 mt-2">Assessment Management Platform</p>
                </div>

                <Card className="shadow-2xl">
                    <CardBody className="p-8">
                        <h2 className="text-xl font-semibold text-slate-900 mb-6">Sign in to your account</h2>

                        {error && (
                            <div className="mb-4 p-3 rounded-lg bg-danger-50 text-danger-600 text-sm">
                                {error}
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                                <Input
                                    type="email"
                                    placeholder="Email address"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="pl-10"
                                    required
                                />
                            </div>

                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                                <Input
                                    type="password"
                                    placeholder="Password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="pl-10"
                                    required
                                />
                            </div>

                            <Button
                                type="submit"
                                variant="primary"
                                size="lg"
                                loading={loading}
                                className="w-full"
                            >
                                Sign In
                            </Button>
                        </form>

                        <div className="mt-6 text-center">
                            <p className="text-sm text-slate-600">
                                Don't have an account?{' '}
                                <Link to="/admin/register" className="text-primary-600 hover:text-primary-700 font-medium">
                                    Register here
                                </Link>
                            </p>
                        </div>
                    </CardBody>
                </Card>
            </div>
        </div>
    );
}
