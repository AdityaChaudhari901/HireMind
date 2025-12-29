import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Input, Button, Card, CardBody } from '../../components/common';
import { Shield, Mail, Lock, User } from 'lucide-react';

export default function AdminRegister() {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        confirmPassword: '',
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const { register } = useAuth();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        if (formData.password.length < 8) {
            setError('Password must be at least 8 characters');
            return;
        }

        setLoading(true);

        try {
            await register({
                name: formData.name,
                email: formData.email,
                password: formData.password,
            });
            navigate('/admin/login', { state: { registered: true } });
        } catch (err) {
            setError(err.response?.data?.detail || 'Registration failed');
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
                    <h1 className="text-3xl font-bold text-white">Create Account</h1>
                    <p className="text-primary-200 mt-2">Join the Assessment Platform</p>
                </div>

                <Card className="shadow-2xl">
                    <CardBody className="p-8">
                        <h2 className="text-xl font-semibold text-slate-900 mb-6">Register as Admin</h2>

                        {error && (
                            <div className="mb-4 p-3 rounded-lg bg-danger-50 text-danger-600 text-sm">
                                {error}
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="relative">
                                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                                <Input
                                    name="name"
                                    type="text"
                                    placeholder="Full name"
                                    value={formData.name}
                                    onChange={handleChange}
                                    className="pl-10"
                                    required
                                />
                            </div>

                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                                <Input
                                    name="email"
                                    type="email"
                                    placeholder="Email address"
                                    value={formData.email}
                                    onChange={handleChange}
                                    className="pl-10"
                                    required
                                />
                            </div>

                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                                <Input
                                    name="password"
                                    type="password"
                                    placeholder="Password (min 8 characters)"
                                    value={formData.password}
                                    onChange={handleChange}
                                    className="pl-10"
                                    required
                                />
                            </div>

                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                                <Input
                                    name="confirmPassword"
                                    type="password"
                                    placeholder="Confirm password"
                                    value={formData.confirmPassword}
                                    onChange={handleChange}
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
                                Create Account
                            </Button>
                        </form>

                        <div className="mt-6 text-center">
                            <p className="text-sm text-slate-600">
                                Already have an account?{' '}
                                <Link to="/admin/login" className="text-primary-600 hover:text-primary-700 font-medium">
                                    Sign in
                                </Link>
                            </p>
                        </div>
                    </CardBody>
                </Card>
            </div>
        </div>
    );
}
