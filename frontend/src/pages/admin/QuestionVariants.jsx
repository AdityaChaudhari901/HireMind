import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { questionsAPI } from '../../services/api';
import { Card, CardBody, CardHeader, Button, Loading, Badge, Input } from '../../components/common';
import {
    LayoutDashboard,
    ArrowLeft,
    Sparkles,
    Check,
    X,
    Plus,
    LogOut
} from 'lucide-react';

export default function QuestionVariants() {
    const { questionId } = useParams();
    const navigate = useNavigate();
    const { admin, logout } = useAuth();

    const [question, setQuestion] = useState(null);
    const [variants, setVariants] = useState([]);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [showAddForm, setShowAddForm] = useState(false);

    const [generateForm, setGenerateForm] = useState({
        baseQuestionText: '',
        options: ['', '', '', ''],
        correctIndex: 0,
        numVariants: 5,
    });

    useEffect(() => {
        loadData();
    }, [questionId]);

    const loadData = async () => {
        try {
            const [questionRes, variantsRes] = await Promise.all([
                questionsAPI.getBaseById(questionId),
                questionsAPI.getVariants(questionId)
            ]);
            setQuestion(questionRes.data);
            setVariants(variantsRes.data);

            // Pre-fill generate form with first variant if exists
            if (variantsRes.data.length > 0) {
                const first = variantsRes.data[0];
                setGenerateForm({
                    baseQuestionText: first.question_text,
                    options: first.options,
                    correctIndex: first.correct_index,
                    numVariants: 5,
                });
            }
        } catch (error) {
            console.error('Failed to load data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleGenerateVariants = async () => {
        setGenerating(true);
        try {
            await questionsAPI.generateVariants({
                question_id: questionId,
                base_question_text: generateForm.baseQuestionText,
                options: generateForm.options,
                correct_index: generateForm.correctIndex,
                num_variants: generateForm.numVariants,
            });
            await loadData();
        } catch (error) {
            console.error('Failed to generate variants:', error);
            alert('Failed to generate variants. Check your Gemini API key.');
        } finally {
            setGenerating(false);
        }
    };

    const handleApprove = async (variantId, approved) => {
        try {
            await questionsAPI.approveVariant(variantId, approved);
            setVariants(variants.map(v =>
                v.id === variantId ? { ...v, approved } : v
            ));
        } catch (error) {
            console.error('Failed to update variant:', error);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-slate-50 flex items-center justify-center">
                <Loading message="Loading variants..." />
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

            {/* Main Content */}
            <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="flex items-center mb-6">
                    <Button variant="secondary" size="sm" onClick={() => navigate('/admin/questions')} className="mr-4">
                        <ArrowLeft className="w-4 h-4" />
                    </Button>
                    <div>
                        <h2 className="text-2xl font-bold text-slate-900">Question Variants</h2>
                        <div className="flex items-center space-x-2 mt-1">
                            <Badge variant="primary">{question?.topic}</Badge>
                            <Badge variant={
                                question?.difficulty === 'Easy' ? 'success' :
                                    question?.difficulty === 'Medium' ? 'warning' : 'danger'
                            }>
                                {question?.difficulty}
                            </Badge>
                        </div>
                    </div>
                </div>

                {/* AI Generation Card */}
                <Card className="mb-6">
                    <CardHeader>
                        <div className="flex items-center justify-between">
                            <h3 className="text-lg font-semibold flex items-center">
                                <Sparkles className="w-5 h-5 text-primary-600 mr-2" />
                                Generate AI Variants
                            </h3>
                        </div>
                    </CardHeader>
                    <CardBody>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">
                                    Base Question Text
                                </label>
                                <textarea
                                    value={generateForm.baseQuestionText}
                                    onChange={(e) => setGenerateForm({ ...generateForm, baseQuestionText: e.target.value })}
                                    placeholder="Enter the base question to generate variants from..."
                                    className="input min-h-[80px]"
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                {generateForm.options.map((opt, i) => (
                                    <div key={i} className="flex items-center space-x-2">
                                        <input
                                            type="radio"
                                            checked={generateForm.correctIndex === i}
                                            onChange={() => setGenerateForm({ ...generateForm, correctIndex: i })}
                                            className="w-4 h-4 text-primary-600"
                                        />
                                        <Input
                                            value={opt}
                                            onChange={(e) => {
                                                const newOpts = [...generateForm.options];
                                                newOpts[i] = e.target.value;
                                                setGenerateForm({ ...generateForm, options: newOpts });
                                            }}
                                            placeholder={`Option ${String.fromCharCode(65 + i)}`}
                                            className="flex-1"
                                        />
                                    </div>
                                ))}
                            </div>

                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-2">
                                    <span className="text-sm text-slate-600">Generate</span>
                                    <select
                                        value={generateForm.numVariants}
                                        onChange={(e) => setGenerateForm({ ...generateForm, numVariants: parseInt(e.target.value) })}
                                        className="input w-20 py-1"
                                    >
                                        {[3, 5, 7, 10].map(n => (
                                            <option key={n} value={n}>{n}</option>
                                        ))}
                                    </select>
                                    <span className="text-sm text-slate-600">variants</span>
                                </div>
                                <Button variant="primary" onClick={handleGenerateVariants} loading={generating}>
                                    <Sparkles className="w-4 h-4 mr-2" />
                                    Generate with AI
                                </Button>
                            </div>
                        </div>
                    </CardBody>
                </Card>

                {/* Variants List */}
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <h3 className="text-lg font-semibold text-slate-900">
                            Variants ({variants.length})
                        </h3>
                    </div>

                    {variants.length === 0 ? (
                        <Card>
                            <CardBody className="text-center py-8">
                                <p className="text-slate-500">No variants yet. Generate some with AI or add manually.</p>
                            </CardBody>
                        </Card>
                    ) : (
                        variants.map((variant, index) => (
                            <Card key={variant.id}>
                                <CardBody>
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <div className="flex items-center space-x-2 mb-2">
                                                <span className="text-sm font-medium text-slate-500">Variant {index + 1}</span>
                                                {variant.is_ai_generated && (
                                                    <Badge variant="primary">AI Generated</Badge>
                                                )}
                                                <Badge variant={variant.approved ? 'success' : 'warning'}>
                                                    {variant.approved ? 'Approved' : 'Pending'}
                                                </Badge>
                                            </div>
                                            <p className="text-slate-900 mb-3">{variant.question_text}</p>
                                            <div className="grid grid-cols-2 gap-2">
                                                {variant.options.map((opt, i) => (
                                                    <div
                                                        key={i}
                                                        className={`px-3 py-2 rounded-lg text-sm ${i === variant.correct_index
                                                                ? 'bg-success-50 text-success-700 border border-success-200'
                                                                : 'bg-slate-100 text-slate-700'
                                                            }`}
                                                    >
                                                        {String.fromCharCode(65 + i)}. {opt}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                        <div className="flex flex-col space-y-2 ml-4">
                                            {!variant.approved ? (
                                                <>
                                                    <Button variant="success" size="sm" onClick={() => handleApprove(variant.id, true)}>
                                                        <Check className="w-4 h-4" />
                                                    </Button>
                                                    <Button variant="danger" size="sm" onClick={() => handleApprove(variant.id, false)}>
                                                        <X className="w-4 h-4" />
                                                    </Button>
                                                </>
                                            ) : (
                                                <Button variant="secondary" size="sm" onClick={() => handleApprove(variant.id, false)}>
                                                    Unapprove
                                                </Button>
                                            )}
                                        </div>
                                    </div>
                                </CardBody>
                            </Card>
                        ))
                    )}
                </div>
            </main>
        </div>
    );
}
