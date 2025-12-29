import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { resultsAPI } from '../../services/api';
import { Card, CardBody, CardHeader, Button, Loading, Badge } from '../../components/common';
import {
    LayoutDashboard,
    Users,
    Download,
    Eye,
    LogOut,
    ChevronDown,
    ChevronUp,
    Trash2
} from 'lucide-react';

export default function Results() {
    const { admin, logout } = useAuth();
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(true);
    const [expandedId, setExpandedId] = useState(null);
    const [detailData, setDetailData] = useState({});

    useEffect(() => {
        loadResults();
    }, []);

    const loadResults = async () => {
        try {
            const res = await resultsAPI.getResults({ limit: 100 });
            setResults(res.data.results);
        } catch (error) {
            console.error('Failed to load results:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleExportCSV = async () => {
        try {
            const res = await resultsAPI.exportCSV();
            const url = window.URL.createObjectURL(new Blob([res.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'test_results.csv');
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error('Failed to export:', error);
        }
    };

    const handleViewDetails = async (sessionId) => {
        if (expandedId === sessionId) {
            setExpandedId(null);
            return;
        }

        try {
            const res = await resultsAPI.getResultDetail(sessionId);
            setDetailData({ ...detailData, [sessionId]: res.data });
            setExpandedId(sessionId);
        } catch (error) {
            console.error('Failed to load details:', error);
        }
    };

    const handleDelete = async (sessionId, e) => {
        e.stopPropagation(); // Prevent card expansion
        if (!confirm('Are you sure you want to delete this result? This action cannot be undone.')) {
            return;
        }
        try {
            await resultsAPI.deleteResult(sessionId);
            await loadResults();
        } catch (error) {
            console.error('Failed to delete result:', error);
            alert(error.response?.data?.detail || 'Failed to delete result');
        }
    };

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
                        <Link to="/admin/dashboard" className="border-b-2 border-transparent text-slate-500 hover:text-slate-700 px-1 py-4 text-sm font-medium">
                            Dashboard
                        </Link>
                        <Link to="/admin/questions" className="border-b-2 border-transparent text-slate-500 hover:text-slate-700 px-1 py-4 text-sm font-medium">
                            Questions
                        </Link>
                        <Link to="/admin/test-links" className="border-b-2 border-transparent text-slate-500 hover:text-slate-700 px-1 py-4 text-sm font-medium">
                            Test Links
                        </Link>
                        <Link to="/admin/results" className="border-b-2 border-primary-500 text-primary-600 px-1 py-4 text-sm font-medium">
                            Results
                        </Link>
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold text-slate-900">Test Results</h2>
                    <Button variant="secondary" onClick={handleExportCSV}>
                        <Download className="w-4 h-4 mr-2" />
                        Export CSV
                    </Button>
                </div>

                {loading ? (
                    <Loading message="Loading results..." />
                ) : results.length === 0 ? (
                    <Card>
                        <CardBody className="text-center py-12">
                            <Users className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                            <h3 className="text-lg font-medium text-slate-900 mb-2">No test results yet</h3>
                            <p className="text-slate-500">Results will appear here when candidates complete tests</p>
                        </CardBody>
                    </Card>
                ) : (
                    <div className="space-y-4">
                        {results.map((result) => (
                            <Card key={result.session_id}>
                                <CardBody>
                                    <div
                                        className="flex items-center justify-between cursor-pointer"
                                        onClick={() => handleViewDetails(result.session_id)}
                                    >
                                        <div className="flex-1">
                                            <div className="flex items-center space-x-3 mb-1">
                                                <h3 className="font-semibold text-slate-900">{result.user_name}</h3>
                                                <Badge variant={
                                                    result.score_percentage >= 70 ? 'success' :
                                                        result.score_percentage >= 50 ? 'warning' : 'danger'
                                                }>
                                                    {result.score_percentage}%
                                                </Badge>
                                                {result.tab_switch_count > 0 && (
                                                    <Badge variant="warning">
                                                        {result.tab_switch_count} tab switches
                                                    </Badge>
                                                )}
                                            </div>
                                            <p className="text-sm text-slate-600">{result.user_email}</p>
                                            <div className="flex items-center space-x-4 mt-2 text-sm text-slate-500">
                                                <span>{result.correct_answers}/{result.total_questions} correct</span>
                                                {result.completed_at && (
                                                    <span>Completed: {new Date(result.completed_at).toLocaleString()}</span>
                                                )}
                                            </div>
                                        </div>
                                        <div className="flex items-center space-x-2">
                                            <Button
                                                variant="danger"
                                                size="sm"
                                                onClick={(e) => handleDelete(result.session_id, e)}
                                            >
                                                <Trash2 className="w-4 h-4 mr-1" />
                                                Delete
                                            </Button>
                                            {expandedId === result.session_id ? (
                                                <ChevronUp className="w-5 h-5 text-slate-400" />
                                            ) : (
                                                <ChevronDown className="w-5 h-5 text-slate-400" />
                                            )}
                                        </div>
                                    </div>

                                    {/* Expanded Details */}
                                    {expandedId === result.session_id && detailData[result.session_id] && (
                                        <div className="mt-4 pt-4 border-t border-slate-200">
                                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                                                <div>
                                                    <p className="text-sm text-slate-500">Total Time</p>
                                                    <p className="font-semibold">{detailData[result.session_id].total_time_seconds.toFixed(1)}s</p>
                                                </div>
                                                <div>
                                                    <p className="text-sm text-slate-500">Avg Time/Question</p>
                                                    <p className="font-semibold">{detailData[result.session_id].average_time_per_question.toFixed(1)}s</p>
                                                </div>
                                                <div>
                                                    <p className="text-sm text-slate-500">Auto-submitted</p>
                                                    <p className="font-semibold">{detailData[result.session_id].auto_submitted_count}</p>
                                                </div>
                                                <div>
                                                    <p className="text-sm text-slate-500">Phone</p>
                                                    <p className="font-semibold">{detailData[result.session_id].user_phone}</p>
                                                </div>
                                            </div>
                                            <div className="text-sm text-slate-500">
                                                <p>IP: {detailData[result.session_id].ip_address || 'N/A'}</p>
                                                <p className="truncate">User Agent: {detailData[result.session_id].user_agent || 'N/A'}</p>
                                            </div>
                                        </div>
                                    )}
                                </CardBody>
                            </Card>
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
}
