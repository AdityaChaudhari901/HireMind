import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { questionsAPI } from '../../services/api';
import { Card, CardBody, CardHeader, Button, Loading, Badge, Input, Select } from '../../components/common';
import {
    LayoutDashboard,
    FileQuestion,
    Link as LinkIcon,
    Plus,
    Trash2,
    Sparkles,
    ChevronRight,
    LogOut,
    Wand2
} from 'lucide-react';

export default function Questions() {
    const { admin, logout } = useAuth();
    const navigate = useNavigate();
    const [questions, setQuestions] = useState([]);
    const [topics, setTopics] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState({ topic: '', difficulty: '' });

    // AI Generation State
    const [showAIGenerate, setShowAIGenerate] = useState(false);
    const [generating, setGenerating] = useState(false);
    const [aiForm, setAiForm] = useState({
        topic: '',
        difficulty: 'Medium',
        num_questions: 10,
        description: ''
    });

    useEffect(() => {
        loadData();
    }, [filter]);

    const loadData = async () => {
        try {
            const [questionsRes, topicsRes] = await Promise.all([
                questionsAPI.getBase(filter),
                questionsAPI.getTopics()
            ]);
            setQuestions(questionsRes.data);
            setTopics(topicsRes.data);
        } catch (error) {
            console.error('Failed to load questions:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id) => {
        if (!confirm('Delete this question and all its variants?')) return;
        try {
            await questionsAPI.deleteBase(id);
            setQuestions(questions.filter(q => q.id !== id));
        } catch (error) {
            console.error('Failed to delete question:', error);
        }
    };

    const handleAIGenerate = async (e) => {
        e.preventDefault();
        if (!aiForm.topic) {
            alert('Please enter a topic');
            return;
        }

        setGenerating(true);
        try {
            const res = await questionsAPI.generateQuestionsFromTopic(aiForm);
            alert(`Successfully generated ${res.data.questions_generated} questions!`);
            setShowAIGenerate(false);
            setAiForm({ topic: '', difficulty: 'Medium', num_questions: 10, description: '' });
            await loadData();
        } catch (error) {
            alert(error.response?.data?.detail || 'Failed to generate questions. Check your Gemini API key.');
        } finally {
            setGenerating(false);
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
                        <Link to="/admin/questions" className="border-b-2 border-primary-500 text-primary-600 px-1 py-4 text-sm font-medium">
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
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold text-slate-900">Question Bank</h2>
                    <div className="flex space-x-3">
                        <Button variant="secondary" onClick={() => setShowAIGenerate(!showAIGenerate)}>
                            <Wand2 className="w-4 h-4 mr-2" />
                            AI Generate
                        </Button>
                        <Button variant="primary" onClick={() => navigate('/admin/questions/new')}>
                            <Plus className="w-4 h-4 mr-2" />
                            Add Manual
                        </Button>
                    </div>
                </div>

                {/* AI Generation Form */}
                {showAIGenerate && (
                    <Card className="mb-6 border-2 border-primary-200 bg-primary-50/30">
                        <CardHeader>
                            <div className="flex items-center space-x-2">
                                <Wand2 className="w-5 h-5 text-primary-600" />
                                <h3 className="text-lg font-semibold text-primary-700">AI Question Generator</h3>
                            </div>
                            <p className="text-sm text-slate-600 mt-1">Generate MCQ questions automatically using AI</p>
                        </CardHeader>
                        <CardBody>
                            <form onSubmit={handleAIGenerate} className="space-y-4">
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <Input
                                        label="Topic *"
                                        value={aiForm.topic}
                                        onChange={(e) => setAiForm({ ...aiForm, topic: e.target.value })}
                                        placeholder="e.g., JavaScript, Python, SQL"
                                        required
                                    />
                                    <Select
                                        label="Difficulty"
                                        value={aiForm.difficulty}
                                        onChange={(e) => setAiForm({ ...aiForm, difficulty: e.target.value })}
                                        options={[
                                            { value: 'Easy', label: 'Easy' },
                                            { value: 'Medium', label: 'Medium' },
                                            { value: 'Hard', label: 'Hard' },
                                        ]}
                                    />
                                    <Input
                                        label="Number of Questions"
                                        type="number"
                                        min="1"
                                        max="100"
                                        value={aiForm.num_questions}
                                        onChange={(e) => setAiForm({ ...aiForm, num_questions: parseInt(e.target.value) })}
                                    />
                                </div>
                                <Input
                                    label="Focus Area (optional)"
                                    value={aiForm.description}
                                    onChange={(e) => setAiForm({ ...aiForm, description: e.target.value })}
                                    placeholder="e.g., Array methods, Async/await, Closures"
                                />
                                <div className="flex justify-end space-x-3">
                                    <Button variant="secondary" type="button" onClick={() => setShowAIGenerate(false)}>
                                        Cancel
                                    </Button>
                                    <Button variant="primary" type="submit" loading={generating}>
                                        <Sparkles className="w-4 h-4 mr-2" />
                                        Generate Questions
                                    </Button>
                                </div>
                            </form>
                        </CardBody>
                    </Card>
                )}

                {/* Filters */}
                <Card className="mb-6">
                    <CardBody>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <Select
                                label="Filter by Topic"
                                value={filter.topic}
                                onChange={(e) => setFilter({ ...filter, topic: e.target.value })}
                                options={[
                                    { value: '', label: 'All Topics' },
                                    ...topics.map(t => ({ value: t, label: t }))
                                ]}
                            />
                            <Select
                                label="Filter by Difficulty"
                                value={filter.difficulty}
                                onChange={(e) => setFilter({ ...filter, difficulty: e.target.value })}
                                options={[
                                    { value: '', label: 'All Difficulties' },
                                    { value: 'Easy', label: 'Easy' },
                                    { value: 'Medium', label: 'Medium' },
                                    { value: 'Hard', label: 'Hard' },
                                ]}
                            />
                        </div>
                    </CardBody>
                </Card>

                {/* Questions List */}
                {loading ? (
                    <Loading message="Loading questions..." />
                ) : questions.length === 0 ? (
                    <Card>
                        <CardBody className="text-center py-12">
                            <FileQuestion className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                            <h3 className="text-lg font-medium text-slate-900 mb-2">No questions yet</h3>
                            <p className="text-slate-500 mb-4">Get started by generating questions with AI</p>
                            <Button variant="primary" onClick={() => setShowAIGenerate(true)}>
                                <Wand2 className="w-4 h-4 mr-2" />
                                Generate with AI
                            </Button>
                        </CardBody>
                    </Card>
                ) : (
                    <div className="space-y-4">
                        {questions.map((question) => (
                            <Card key={question.id}>
                                <CardBody>
                                    <div className="flex items-center justify-between">
                                        <div className="flex-1">
                                            <div className="flex items-center space-x-3 mb-2">
                                                <Badge variant={
                                                    question.difficulty === 'Easy' ? 'success' :
                                                        question.difficulty === 'Medium' ? 'warning' : 'danger'
                                                }>
                                                    {question.difficulty}
                                                </Badge>
                                                <Badge variant="primary">{question.topic}</Badge>
                                                <span className="text-sm text-slate-500">
                                                    {question.variant_count} variant{question.variant_count !== 1 ? 's' : ''}
                                                </span>
                                            </div>
                                            <p className="text-slate-700">{question.description || 'No description'}</p>
                                        </div>
                                        <div className="flex items-center space-x-2 ml-4">
                                            <Button
                                                variant="secondary"
                                                size="sm"
                                                onClick={() => navigate(`/admin/questions/${question.id}/variants`)}
                                            >
                                                <Sparkles className="w-4 h-4 mr-1" />
                                                Variants
                                            </Button>
                                            <Button
                                                variant="danger"
                                                size="sm"
                                                onClick={() => handleDelete(question.id)}
                                            >
                                                <Trash2 className="w-4 h-4" />
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
