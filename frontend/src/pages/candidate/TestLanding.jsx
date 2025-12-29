import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { testAPI } from '../../services/api';
import { Card, CardBody, Button, Input, Loading } from '../../components/common';
import { ClipboardCheck, Clock, AlertCircle, ChevronRight } from 'lucide-react';

export default function TestLanding() {
    const { linkId } = useParams();
    const navigate = useNavigate();

    const [testInfo, setTestInfo] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [starting, setStarting] = useState(false);
    const [showForm, setShowForm] = useState(false);

    const [formData, setFormData] = useState({
        name: '',
        email: '',
        phone: '',
    });

    useEffect(() => {
        validateLink();
    }, [linkId]);

    const validateLink = async () => {
        try {
            const res = await testAPI.validateLink(linkId);
            setTestInfo(res.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Invalid or expired test link');
        } finally {
            setLoading(false);
        }
    };

    const handleStartTest = async (e) => {
        e.preventDefault();
        setStarting(true);

        try {
            const res = await testAPI.startTest(linkId, {
                name: formData.name,
                email: formData.email,
                phone: formData.phone,
            });

            // Store session ID and navigate to test
            sessionStorage.setItem('testSessionId', res.data.session_id);
            sessionStorage.setItem('testConfig', JSON.stringify({
                totalQuestions: res.data.total_questions,
                timePerQuestion: res.data.time_per_question,
            }));

            navigate(`/test/${linkId}/take`);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to start test');
            setStarting(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900 flex items-center justify-center p-4">
                <Loading message="Validating test link..." />
            </div>
        );
    }

    if (error && !testInfo) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900 flex items-center justify-center p-4">
                <Card className="max-w-md w-full">
                    <CardBody className="p-8 text-center">
                        <AlertCircle className="w-16 h-16 text-danger-500 mx-auto mb-4" />
                        <h2 className="text-xl font-bold text-slate-900 mb-2">Link Not Valid</h2>
                        <p className="text-slate-600">{error}</p>
                    </CardBody>
                </Card>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900 flex items-center justify-center p-4">
            <div className="max-w-lg w-full">
                {!showForm ? (
                    /* Instructions Screen */
                    <Card className="shadow-2xl">
                        <CardBody className="p-8">
                            <div className="text-center mb-6">
                                <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary-100 mb-4">
                                    <ClipboardCheck className="w-8 h-8 text-primary-600" />
                                </div>
                                <h1 className="text-2xl font-bold text-slate-900">{testInfo?.test_name}</h1>
                                <p className="text-slate-600 mt-2">Online Assessment</p>
                            </div>

                            <div className="space-y-4 mb-8">
                                <div className="flex items-start space-x-3 p-4 bg-slate-50 rounded-lg">
                                    <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 font-semibold">
                                        {testInfo?.total_questions}
                                    </div>
                                    <div>
                                        <h3 className="font-medium text-slate-900">Total Questions</h3>
                                        <p className="text-sm text-slate-600">Multiple choice questions</p>
                                    </div>
                                </div>

                                <div className="flex items-start space-x-3 p-4 bg-slate-50 rounded-lg">
                                    <div className="flex-shrink-0 w-8 h-8 bg-warning-50 rounded-full flex items-center justify-center">
                                        <Clock className="w-4 h-4 text-warning-600" />
                                    </div>
                                    <div>
                                        <h3 className="font-medium text-slate-900">{testInfo?.time_per_question} Seconds Per Question</h3>
                                        <p className="text-sm text-slate-600">Auto-submits when time runs out</p>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-warning-50 border border-warning-200 rounded-lg p-4 mb-6">
                                <h3 className="font-semibold text-warning-800 mb-2">⚠️ Important Rules</h3>
                                <ul className="text-sm text-warning-700 space-y-1">
                                    <li>• One question at a time</li>
                                    <li>• You cannot go back to previous questions</li>
                                    <li>• Timer auto-submits your answer</li>
                                    <li>• Do not refresh or switch tabs</li>
                                    <li>• Test will be monitored for suspicious activity</li>
                                </ul>
                            </div>

                            <Button
                                variant="primary"
                                size="lg"
                                className="w-full"
                                onClick={() => setShowForm(true)}
                            >
                                Continue to Registration
                                <ChevronRight className="w-5 h-5 ml-2" />
                            </Button>
                        </CardBody>
                    </Card>
                ) : (
                    /* Registration Form */
                    <Card className="shadow-2xl">
                        <CardBody className="p-8">
                            <h2 className="text-xl font-bold text-slate-900 mb-6">Enter Your Details</h2>

                            {error && (
                                <div className="mb-4 p-3 rounded-lg bg-danger-50 text-danger-600 text-sm">
                                    {error}
                                </div>
                            )}

                            <form onSubmit={handleStartTest} className="space-y-4">
                                <Input
                                    label="Full Name"
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    placeholder="Enter your full name"
                                    required
                                />

                                <Input
                                    label="Email Address"
                                    type="email"
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    placeholder="Enter your email"
                                    required
                                />

                                <Input
                                    label="Phone Number"
                                    type="tel"
                                    value={formData.phone}
                                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                    placeholder="Enter your phone number"
                                    required
                                />

                                <div className="pt-4 flex space-x-3">
                                    <Button
                                        variant="secondary"
                                        type="button"
                                        onClick={() => setShowForm(false)}
                                        className="flex-1"
                                    >
                                        Back
                                    </Button>
                                    <Button
                                        variant="primary"
                                        size="lg"
                                        type="submit"
                                        loading={starting}
                                        className="flex-1"
                                    >
                                        Start Test
                                    </Button>
                                </div>
                            </form>
                        </CardBody>
                    </Card>
                )}
            </div>
        </div>
    );
}
