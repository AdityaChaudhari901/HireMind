import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { testAPI } from '../../services/api';
import { Card, CardBody, CardHeader, Button, Loading, Badge, Input, Select } from '../../components/common';
import {
    LayoutDashboard,
    Link as LinkIcon,
    Plus,
    Copy,
    CheckCircle,
    LogOut,
    Trash2
} from 'lucide-react';

export default function TestLinks() {
    const { admin, logout } = useAuth();
    const navigate = useNavigate();
    const [links, setLinks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showCreate, setShowCreate] = useState(false);
    const [creating, setCreating] = useState(false);
    const [copiedId, setCopiedId] = useState(null);

    const [formData, setFormData] = useState({
        testName: 'Assessment Test',
        totalQuestions: 60,
        timePerQuestion: 10,
        topics: '',
        expiresHours: 72,
        maxUses: 0,  // 0 = unlimited
    });

    useEffect(() => {
        loadLinks();
    }, []);

    const loadLinks = async () => {
        try {
            const res = await testAPI.getLinks({ limit: 100 });
            setLinks(res.data);
        } catch (error) {
            console.error('Failed to load links:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreate = async (e) => {
        e.preventDefault();
        setCreating(true);
        try {
            const topicsArray = formData.topics
                ? formData.topics.split(',').map(t => t.trim()).filter(Boolean)
                : [];

            await testAPI.generateLink({
                test_name: formData.testName,
                total_questions: parseInt(formData.totalQuestions),
                time_per_question: parseInt(formData.timePerQuestion),
                topics: topicsArray,
                expires_hours: parseInt(formData.expiresHours),
                max_uses: parseInt(formData.maxUses),
            });

            await loadLinks();
            setShowCreate(false);
        } catch (error) {
            console.error('Failed to create link:', error);
            alert(error.response?.data?.detail || 'Failed to create test link');
        } finally {
            setCreating(false);
        }
    };

    const copyToClipboard = (link) => {
        navigator.clipboard.writeText(link.full_url);
        setCopiedId(link.link_id);
        setTimeout(() => setCopiedId(null), 2000);
    };

    const handleDelete = async (linkId) => {
        if (!confirm('Are you sure you want to delete this test link?')) {
            return;
        }
        try {
            await testAPI.deleteLink(linkId);
            await loadLinks();
        } catch (error) {
            console.error('Failed to delete link:', error);
            alert(error.response?.data?.detail || 'Failed to delete test link');
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
                        <Link to="/admin/test-links" className="border-b-2 border-primary-500 text-primary-600 px-1 py-4 text-sm font-medium">
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
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold text-slate-900">Test Links</h2>
                    <Button variant="primary" onClick={() => setShowCreate(!showCreate)}>
                        <Plus className="w-4 h-4 mr-2" />
                        Generate Link
                    </Button>
                </div>

                {/* Create Form */}
                {showCreate && (
                    <Card className="mb-6">
                        <CardHeader>
                            <h3 className="text-lg font-semibold">Generate New Test Link</h3>
                        </CardHeader>
                        <CardBody>
                            <form onSubmit={handleCreate} className="space-y-4">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <Input
                                        label="Test Name"
                                        value={formData.testName}
                                        onChange={(e) => setFormData({ ...formData, testName: e.target.value })}
                                        required
                                    />
                                    <Input
                                        label="Total Questions"
                                        type="number"
                                        min="1"
                                        max="100"
                                        value={formData.totalQuestions}
                                        onChange={(e) => setFormData({ ...formData, totalQuestions: e.target.value })}
                                        required
                                    />
                                    <Input
                                        label="Time per Question (seconds)"
                                        type="number"
                                        min="5"
                                        max="60"
                                        value={formData.timePerQuestion}
                                        onChange={(e) => setFormData({ ...formData, timePerQuestion: e.target.value })}
                                        required
                                    />
                                    <Input
                                        label="Expires in (hours)"
                                        type="number"
                                        min="1"
                                        max="720"
                                        value={formData.expiresHours}
                                        onChange={(e) => setFormData({ ...formData, expiresHours: e.target.value })}
                                        required
                                    />
                                    <Input
                                        label="Max Uses (0 = Unlimited)"
                                        type="number"
                                        min="0"
                                        value={formData.maxUses}
                                        onChange={(e) => setFormData({ ...formData, maxUses: e.target.value })}
                                        required
                                    />
                                </div>
                                <Input
                                    label="Topics (comma-separated, leave empty for all)"
                                    value={formData.topics}
                                    onChange={(e) => setFormData({ ...formData, topics: e.target.value })}
                                    placeholder="e.g., JavaScript, Python, SQL"
                                />
                                <div className="flex justify-end space-x-3">
                                    <Button variant="secondary" type="button" onClick={() => setShowCreate(false)}>
                                        Cancel
                                    </Button>
                                    <Button variant="primary" type="submit" loading={creating}>
                                        Generate Link
                                    </Button>
                                </div>
                            </form>
                        </CardBody>
                    </Card>
                )}

                {/* Links List */}
                {loading ? (
                    <Loading message="Loading test links..." />
                ) : links.length === 0 ? (
                    <Card>
                        <CardBody className="text-center py-12">
                            <LinkIcon className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                            <h3 className="text-lg font-medium text-slate-900 mb-2">No test links yet</h3>
                            <p className="text-slate-500 mb-4">Generate a link to share with candidates</p>
                            <Button variant="primary" onClick={() => setShowCreate(true)}>
                                <Plus className="w-4 h-4 mr-2" />
                                Generate Link
                            </Button>
                        </CardBody>
                    </Card>
                ) : (
                    <div className="space-y-4">
                        {links.map((link) => (
                            <Card key={link.link_id}>
                                <CardBody>
                                    <div className="flex items-center justify-between">
                                        <div className="flex-1">
                                            <div className="flex items-center space-x-3 mb-2">
                                                <h3 className="font-semibold text-slate-900">{link.test_name}</h3>
                                                <Badge variant={link.is_used ? 'default' : 'success'}>
                                                    {link.max_uses === 0
                                                        ? `${link.current_uses} used (Unlimited)`
                                                        : `${link.current_uses}/${link.max_uses} used`}
                                                </Badge>
                                            </div>
                                            <p className="text-sm text-slate-600 mb-2">
                                                {link.total_questions} questions • {link.time_per_question}s per question
                                                {link.topics.length > 0 && ` • Topics: ${link.topics.join(', ')}`}
                                            </p>
                                            <div className="flex items-center space-x-2">
                                                <code className="text-xs bg-slate-100 px-2 py-1 rounded">
                                                    {link.full_url}
                                                </code>
                                                <Button
                                                    variant="secondary"
                                                    size="sm"
                                                    onClick={() => copyToClipboard(link)}
                                                >
                                                    {copiedId === link.link_id ? (
                                                        <CheckCircle className="w-4 h-4 text-success-600" />
                                                    ) : (
                                                        <Copy className="w-4 h-4" />
                                                    )}
                                                </Button>
                                            </div>
                                        </div>
                                        <div className="flex flex-col items-end gap-2">
                                            <div className="text-right text-sm text-slate-500">
                                                <p>Created: {new Date(link.created_at).toLocaleDateString()}</p>
                                                {link.expires_at && (
                                                    <p>Expires: {new Date(link.expires_at).toLocaleDateString()}</p>
                                                )}
                                            </div>
                                            <Button
                                                variant="danger"
                                                size="sm"
                                                onClick={() => handleDelete(link.link_id)}
                                            >
                                                <Trash2 className="w-4 h-4 mr-1" />
                                                Delete
                                            </Button>
                                        </div>
                                    </div>
                                </CardBody>
                            </Card>
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
}
