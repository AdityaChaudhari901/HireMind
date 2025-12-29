import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { questionsAPI, testAPI, resultsAPI } from '../../services/api';
import { Card, CardBody, CardHeader, Button, Loading, Badge } from '../../components/common';
import {
    LayoutDashboard,
    FileQuestion,
    Link as LinkIcon,
    Users,
    TrendingUp,
    Plus,
    ExternalLink,
    LogOut
} from 'lucide-react';

export default function Dashboard() {
    const { admin, logout } = useAuth();
    const [stats, setStats] = useState(null);
    const [recentResults, setRecentResults] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            const [statsRes, resultsRes] = await Promise.all([
                questionsAPI.getStats(),
                resultsAPI.getResults({ limit: 5 })
            ]);
            setStats(statsRes.data);
            setRecentResults(resultsRes.data.results);
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-slate-50 flex items-center justify-center">
                <Loading message="Loading dashboard..." />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-50">
            {/* Header */}
            <header className="bg-white border-b border-slate-200">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <div className="flex items-center space-x-3">
                            <LayoutDashboard className="w-8 h-8 text-primary-600" />
                            <h1 className="text-xl font-bold text-slate-900">Assessment Platform</h1>
                        </div>
                        <div className="flex items-center space-x-4">
                            <span className="text-sm text-slate-600">Welcome, {admin?.name}</span>
                            <Button variant="secondary" size="sm" onClick={logout}>
                                <LogOut className="w-4 h-4 mr-2" />
                                Logout
                            </Button>
                        </div>
                    </div>
                </div>
            </header>

            {/* Navigation */}
            <nav className="bg-white border-b border-slate-200">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex space-x-8">
                        <Link to="/admin/dashboard" className="border-b-2 border-primary-500 text-primary-600 px-1 py-4 text-sm font-medium">
                            Dashboard
                        </Link>
                        <Link to="/admin/questions" className="border-b-2 border-transparent text-slate-500 hover:text-slate-700 px-1 py-4 text-sm font-medium">
                            Questions
                        </Link>
                        <Link to="/admin/test-links" className="border-b-2 border-transparent text-slate-500 hover:text-slate-700 px-1 py-4 text-sm font-medium">
                            Test Links
                        </Link>
                        <Link to="/admin/results" className="border-b-2 border-transparent text-slate-500 hover:text-slate-700 px-1 py-4 text-sm font-medium">
                            Results
                        </Link>
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <Card>
                        <CardBody>
                            <div className="flex items-center">
                                <div className="flex-shrink-0 p-3 bg-primary-100 rounded-lg">
                                    <FileQuestion className="w-6 h-6 text-primary-600" />
                                </div>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-slate-600">Base Questions</p>
                                    <p className="text-2xl font-bold text-slate-900">{stats?.total_base_questions || 0}</p>
                                </div>
                            </div>
                        </CardBody>
                    </Card>

                    <Card>
                        <CardBody>
                            <div className="flex items-center">
                                <div className="flex-shrink-0 p-3 bg-success-50 rounded-lg">
                                    <TrendingUp className="w-6 h-6 text-success-600" />
                                </div>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-slate-600">Approved Variants</p>
                                    <p className="text-2xl font-bold text-slate-900">{stats?.approved_variants || 0}</p>
                                </div>
                            </div>
                        </CardBody>
                    </Card>

                    <Card>
                        <CardBody>
                            <div className="flex items-center">
                                <div className="flex-shrink-0 p-3 bg-warning-50 rounded-lg">
                                    <LinkIcon className="w-6 h-6 text-warning-600" />
                                </div>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-slate-600">Pending Approval</p>
                                    <p className="text-2xl font-bold text-slate-900">{stats?.pending_variants || 0}</p>
                                </div>
                            </div>
                        </CardBody>
                    </Card>

                    <Card>
                        <CardBody>
                            <div className="flex items-center">
                                <div className="flex-shrink-0 p-3 bg-purple-100 rounded-lg">
                                    <Users className="w-6 h-6 text-purple-600" />
                                </div>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-slate-600">Total Variants</p>
                                    <p className="text-2xl font-bold text-slate-900">{stats?.total_variants || 0}</p>
                                </div>
                            </div>
                        </CardBody>
                    </Card>
                </div>

                {/* Quick Actions */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                    <Card>
                        <CardHeader>
                            <h2 className="text-lg font-semibold text-slate-900">Quick Actions</h2>
                        </CardHeader>
                        <CardBody className="space-y-3">
                            <Link to="/admin/questions/new" className="flex items-center justify-between p-3 rounded-lg hover:bg-slate-50 transition-colors">
                                <div className="flex items-center">
                                    <Plus className="w-5 h-5 text-primary-600 mr-3" />
                                    <span className="font-medium">Add New Question</span>
                                </div>
                                <ExternalLink className="w-4 h-4 text-slate-400" />
                            </Link>
                            <Link to="/admin/test-links/new" className="flex items-center justify-between p-3 rounded-lg hover:bg-slate-50 transition-colors">
                                <div className="flex items-center">
                                    <LinkIcon className="w-5 h-5 text-primary-600 mr-3" />
                                    <span className="font-medium">Generate Test Link</span>
                                </div>
                                <ExternalLink className="w-4 h-4 text-slate-400" />
                            </Link>
                            <Link to="/admin/pending" className="flex items-center justify-between p-3 rounded-lg hover:bg-slate-50 transition-colors">
                                <div className="flex items-center">
                                    <FileQuestion className="w-5 h-5 text-warning-600 mr-3" />
                                    <span className="font-medium">Review Pending Variants</span>
                                </div>
                                <Badge variant="warning">{stats?.pending_variants || 0}</Badge>
                            </Link>
                        </CardBody>
                    </Card>

                    <Card>
                        <CardHeader>
                            <div className="flex items-center justify-between">
                                <h2 className="text-lg font-semibold text-slate-900">Recent Results</h2>
                                <Link to="/admin/results" className="text-sm text-primary-600 hover:text-primary-700">
                                    View all
                                </Link>
                            </div>
                        </CardHeader>
                        <CardBody>
                            {recentResults.length === 0 ? (
                                <p className="text-center text-slate-500 py-4">No test results yet</p>
                            ) : (
                                <div className="space-y-3">
                                    {recentResults.map((result) => (
                                        <div key={result.session_id} className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
                                            <div>
                                                <p className="font-medium text-slate-900">{result.user_name}</p>
                                                <p className="text-sm text-slate-500">{result.user_email}</p>
                                            </div>
                                            <Badge variant={result.score_percentage >= 70 ? 'success' : result.score_percentage >= 50 ? 'warning' : 'danger'}>
                                                {result.score_percentage}%
                                            </Badge>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </CardBody>
                    </Card>
                </div>
            </main>
        </div>
    );
}
