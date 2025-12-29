import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { questionsAPI } from '../../services/api';
import { Card, CardBody, Button, Input, Select } from '../../components/common';
import { LayoutDashboard, ArrowLeft, Plus, Trash2, LogOut } from 'lucide-react';

export default function NewQuestion() {
    const { admin, logout } = useAuth();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const [formData, setFormData] = useState({
        topic: '',
        difficulty: 'Medium',
        description: '',
        questionText: '',
        options: ['', '', '', ''],
        correctIndex: 0,
    });

    const handleOptionChange = (index, value) => {
        const newOptions = [...formData.options];
        newOptions[index] = value;
        setFormData({ ...formData, options: newOptions });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            // Create base question
            const baseRes = await questionsAPI.createBase({
                topic: formData.topic,
                difficulty: formData.difficulty,
                description: formData.description,
            });

            // Create first variant
            await questionsAPI.createVariant({
                question_id: baseRes.data.id,
                question_text: formData.questionText,
                options: formData.options,
                correct_index: parseInt(formData.correctIndex),
            });

            navigate('/admin/questions');
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to create question');
        } finally {
            setLoading(false);
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

            {/* Main Content */}
            <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="flex items-center mb-6">
                    <Button variant="secondary" size="sm" onClick={() => navigate('/admin/questions')} className="mr-4">
                        <ArrowLeft className="w-4 h-4" />
                    </Button>
                    <h2 className="text-2xl font-bold text-slate-900">Add New Question</h2>
                </div>

                <Card>
                    <CardBody className="p-6">
                        {error && (
                            <div className="mb-4 p-3 rounded-lg bg-danger-50 text-danger-600 text-sm">
                                {error}
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className="space-y-6">
                            {/* Base Question Info */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <Input
                                    label="Topic"
                                    value={formData.topic}
                                    onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                                    placeholder="e.g., JavaScript, Python, SQL"
                                    required
                                />
                                <Select
                                    label="Difficulty"
                                    value={formData.difficulty}
                                    onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                                    options={[
                                        { value: 'Easy', label: 'Easy' },
                                        { value: 'Medium', label: 'Medium' },
                                        { value: 'Hard', label: 'Hard' },
                                    ]}
                                />
                            </div>

                            <Input
                                label="Description (optional)"
                                value={formData.description}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                placeholder="Brief description of what this question tests"
                            />

                            {/* Question Text */}
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">
                                    Question Text
                                </label>
                                <textarea
                                    value={formData.questionText}
                                    onChange={(e) => setFormData({ ...formData, questionText: e.target.value })}
                                    placeholder="Enter the question text..."
                                    className="input min-h-[100px]"
                                    required
                                />
                            </div>

                            {/* Options */}
                            <div className="space-y-3">
                                <label className="block text-sm font-medium text-slate-700">
                                    Options (select the correct answer)
                                </label>
                                {formData.options.map((option, index) => (
                                    <div key={index} className="flex items-center space-x-3">
                                        <input
                                            type="radio"
                                            name="correctAnswer"
                                            checked={formData.correctIndex === index}
                                            onChange={() => setFormData({ ...formData, correctIndex: index })}
                                            className="w-4 h-4 text-primary-600"
                                        />
                                        <Input
                                            value={option}
                                            onChange={(e) => handleOptionChange(index, e.target.value)}
                                            placeholder={`Option ${String.fromCharCode(65 + index)}`}
                                            className="flex-1"
                                            required
                                        />
                                    </div>
                                ))}
                            </div>

                            <div className="flex justify-end space-x-3 pt-4">
                                <Button variant="secondary" type="button" onClick={() => navigate('/admin/questions')}>
                                    Cancel
                                </Button>
                                <Button variant="primary" type="submit" loading={loading}>
                                    <Plus className="w-4 h-4 mr-2" />
                                    Create Question
                                </Button>
                            </div>
                        </form>
                    </CardBody>
                </Card>
            </main>
        </div>
    );
}
