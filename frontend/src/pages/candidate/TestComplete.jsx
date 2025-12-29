import { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardBody } from '../../components/common';
import { CheckCircle } from 'lucide-react';

export default function TestComplete() {
    const { linkId } = useParams();

    useEffect(() => {
        // Clear session data
        sessionStorage.removeItem('testSessionId');
        sessionStorage.removeItem('testConfig');
    }, []);

    return (
        <div className="min-h-screen bg-gradient-to-br from-success-500 via-primary-600 to-primary-900 flex items-center justify-center p-4">
            <Card className="max-w-md w-full shadow-2xl">
                <CardBody className="p-8 text-center">
                    <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-success-100 mb-6">
                        <CheckCircle className="w-10 h-10 text-success-600" />
                    </div>

                    <h1 className="text-2xl font-bold text-slate-900 mb-4">
                        Test Completed!
                    </h1>

                    <p className="text-slate-600 mb-6">
                        Thank you for completing the assessment. Your responses have been recorded successfully.
                    </p>

                    <div className="bg-slate-50 rounded-lg p-4 text-left">
                        <h3 className="font-semibold text-slate-900 mb-2">What's Next?</h3>
                        <ul className="text-sm text-slate-600 space-y-1">
                            <li>• Your results will be reviewed by the hiring team</li>
                            <li>• You will be contacted via email regarding the next steps</li>
                            <li>• Please do not share the test link with others</li>
                        </ul>
                    </div>

                    <p className="text-sm text-slate-500 mt-6">
                        You may now close this window.
                    </p>
                </CardBody>
            </Card>
        </div>
    );
}
