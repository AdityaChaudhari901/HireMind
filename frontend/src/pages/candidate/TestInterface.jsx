import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { testAPI } from '../../services/api';
import { useTimer, useAntiCheat } from '../../hooks/useTimer';
import { Card, CardBody, Button, Loading } from '../../components/common';
import { AlertCircle, Clock } from 'lucide-react';

export default function TestInterface() {
    const { linkId } = useParams();
    const navigate = useNavigate();

    const [question, setQuestion] = useState(null);
    const [selectedIndex, setSelectedIndex] = useState(null);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState('');

    // Total test timer state
    const [totalTimeLeft, setTotalTimeLeft] = useState(null);
    const totalTimerRef = useRef(null);

    const sessionId = sessionStorage.getItem('testSessionId');
    const testConfig = JSON.parse(sessionStorage.getItem('testConfig') || '{}');
    const timePerQuestion = testConfig.timePerQuestion || 10;
    const totalQuestions = testConfig.totalQuestions || 60;
    const totalTestTime = totalQuestions * timePerQuestion; // Total seconds for entire test

    // Initialize total timer on first load
    useEffect(() => {
        if (totalTimeLeft === null) {
            const savedTime = sessionStorage.getItem('totalTimeLeft');
            setTotalTimeLeft(savedTime ? parseInt(savedTime) : totalTestTime);
        }
    }, [totalTestTime]);

    // Total test timer countdown
    useEffect(() => {
        if (totalTimeLeft === null || totalTimeLeft <= 0) return;

        totalTimerRef.current = setInterval(() => {
            setTotalTimeLeft(prev => {
                const newTime = prev - 1;
                sessionStorage.setItem('totalTimeLeft', newTime.toString());
                if (newTime <= 0) {
                    clearInterval(totalTimerRef.current);
                    // Auto-submit test when total time expires
                    handleAutoSubmitTest();
                }
                return newTime;
            });
        }, 1000);

        return () => clearInterval(totalTimerRef.current);
    }, [totalTimeLeft !== null]);

    // Auto-submit entire test when time runs out
    const handleAutoSubmitTest = async () => {
        try {
            await testAPI.submitAnswer(sessionId, selectedIndex);
            navigate(`/test/${linkId}/complete`);
        } catch (e) {
            navigate(`/test/${linkId}/complete`);
        }
    };

    // Format total time as MM:SS
    const formatTime = (seconds) => {
        if (!seconds || seconds < 0) return '00:00';
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    // Auto-submit when per-question timer expires
    const handleTimeExpire = useCallback(() => {
        if (!submitting) {
            handleSubmit(true);
        }
    }, [submitting]);

    const { timeLeft, percentage, start, stop, reset } = useTimer(timePerQuestion, handleTimeExpire);

    // Anti-cheat measures
    const handleTabSwitch = useCallback(async () => {
        if (sessionId) {
            try {
                await testAPI.logTabSwitch(sessionId);
            } catch (e) {
                console.error('Failed to log tab switch');
            }
        }
    }, [sessionId]);

    useAntiCheat(sessionId, handleTabSwitch);

    useEffect(() => {
        if (!sessionId) {
            navigate(`/test/${linkId}`);
            return;
        }
        loadQuestion();
    }, [sessionId, linkId]);

    const loadQuestion = async () => {
        try {
            const res = await testAPI.getQuestion(sessionId);
            setQuestion(res.data);
            setSelectedIndex(null);
            reset(res.data.time_remaining || timePerQuestion);
            start(res.data.time_remaining || timePerQuestion);
            setLoading(false);
        } catch (err) {
            if (err.response?.data?.detail === 'No more questions' ||
                err.response?.data?.detail === 'Test already completed') {
                navigate(`/test/${linkId}/complete`);
            } else {
                setError(err.response?.data?.detail || 'Failed to load question');
            }
        }
    };

    const handleSubmit = async (autoSubmit = false) => {
        if (submitting) return;
        setSubmitting(true);
        stop();

        try {
            const res = await testAPI.submitAnswer(sessionId, selectedIndex);

            if (res.data.test_completed) {
                navigate(`/test/${linkId}/complete`);
            } else if (res.data.next_question) {
                setQuestion(res.data.next_question);
                setSelectedIndex(null);
                reset(res.data.next_question.time_remaining || timePerQuestion);
                start(res.data.next_question.time_remaining || timePerQuestion);
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to submit answer');
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-slate-100 flex items-center justify-center">
                <Loading message="Loading question..." />
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4">
                <Card className="max-w-md w-full">
                    <CardBody className="p-8 text-center">
                        <AlertCircle className="w-16 h-16 text-danger-500 mx-auto mb-4" />
                        <h2 className="text-xl font-bold text-slate-900 mb-2">Error</h2>
                        <p className="text-slate-600">{error}</p>
                    </CardBody>
                </Card>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-100 no-select">
            {/* Total Test Timer - Fixed at top */}
            <div className={`sticky top-0 z-20 py-2 px-4 text-center ${totalTimeLeft <= 60 ? 'bg-danger-500' :
                    totalTimeLeft <= 120 ? 'bg-warning-500' : 'bg-primary-600'
                }`}>
                <div className="flex items-center justify-center space-x-2">
                    <Clock className="w-5 h-5 text-white" />
                    <span className="text-white font-bold text-lg">
                        Time Remaining: {formatTime(totalTimeLeft)}
                    </span>
                </div>
            </div>

            {/* Header with Question Timer */}
            <header className="bg-white border-b border-slate-200 sticky top-10 z-10">
                <div className="max-w-4xl mx-auto px-4 py-3">
                    <div className="flex items-center justify-between">
                        <div>
                            <span className="text-sm text-slate-500">Question</span>
                            <span className="ml-2 font-bold text-slate-900">
                                {question?.question_number} / {question?.total_questions}
                            </span>
                        </div>

                        {/* Per-Question Timer */}
                        <div className="flex items-center space-x-3">
                            <span className="text-sm text-slate-500">Question Timer:</span>
                            <div className={`text-2xl font-bold ${timeLeft <= 3 ? 'text-danger-500 animate-pulse' :
                                timeLeft <= 5 ? 'text-warning-500' : 'text-primary-600'
                                }`}>
                                {timeLeft}s
                            </div>
                        </div>
                    </div>

                    {/* Timer Bar */}
                    <div className="mt-2 h-2 bg-slate-200 rounded-full overflow-hidden">
                        <div
                            className={`h-full transition-all duration-200 ${percentage <= 30 ? 'bg-danger-500' :
                                percentage <= 50 ? 'bg-warning-500' : 'bg-success-500'
                                }`}
                            style={{ width: `${percentage}%` }}
                        />
                    </div>
                </div>
            </header>

            {/* Question Content */}
            <main className="max-w-4xl mx-auto px-4 py-8">
                <Card className="shadow-lg">
                    <CardBody className="p-8">
                        {/* Question Text */}
                        <div className="mb-8">
                            <h2 className="text-xl font-semibold text-slate-900 leading-relaxed">
                                {question?.question_text}
                            </h2>
                        </div>

                        {/* Options */}
                        <div className="space-y-3 mb-8">
                            {question?.options.map((option, index) => (
                                <button
                                    key={index}
                                    onClick={() => setSelectedIndex(index)}
                                    disabled={submitting}
                                    className={`option-btn ${selectedIndex === index ? 'option-btn-selected' : ''}`}
                                >
                                    <div className="flex items-center">
                                        <span className={`w-8 h-8 rounded-full flex items-center justify-center mr-4 text-sm font-semibold ${selectedIndex === index
                                            ? 'bg-primary-500 text-white'
                                            : 'bg-slate-100 text-slate-600'
                                            }`}>
                                            {String.fromCharCode(65 + index)}
                                        </span>
                                        <span className="text-slate-900">{option}</span>
                                    </div>
                                </button>
                            ))}
                        </div>

                        {/* Submit Button */}
                        <div className="flex justify-end">
                            <Button
                                variant="primary"
                                size="lg"
                                onClick={() => handleSubmit(false)}
                                loading={submitting}
                                disabled={submitting}
                            >
                                {question?.question_number === question?.total_questions ? 'Submit & Finish' : 'Submit & Next'}
                            </Button>
                        </div>
                    </CardBody>
                </Card>
            </main>

            {/* Progress indicator */}
            <div className="fixed bottom-4 left-1/2 -translate-x-1/2">
                <div className="flex space-x-1">
                    {Array.from({ length: Math.min(question?.total_questions || 0, 20) }).map((_, i) => (
                        <div
                            key={i}
                            className={`w-2 h-2 rounded-full ${i < (question?.question_number || 0) - 1 ? 'bg-primary-500' :
                                i === (question?.question_number || 0) - 1 ? 'bg-primary-400 animate-pulse' :
                                    'bg-slate-300'
                                }`}
                        />
                    ))}
                    {(question?.total_questions || 0) > 20 && (
                        <span className="text-xs text-slate-500 ml-2">
                            +{(question?.total_questions || 0) - 20} more
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
}
