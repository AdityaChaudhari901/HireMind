import { useState, useEffect, useCallback, useRef } from 'react';

export function useTimer(initialSeconds = 10, onExpire) {
    const [timeLeft, setTimeLeft] = useState(initialSeconds);
    const [isRunning, setIsRunning] = useState(false);
    const intervalRef = useRef(null);
    const onExpireRef = useRef(onExpire);

    // Keep callback ref updated
    useEffect(() => {
        onExpireRef.current = onExpire;
    }, [onExpire]);

    const start = useCallback((seconds = initialSeconds) => {
        setTimeLeft(seconds);
        setIsRunning(true);
    }, [initialSeconds]);

    const stop = useCallback(() => {
        setIsRunning(false);
        if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
        }
    }, []);

    const reset = useCallback((seconds = initialSeconds) => {
        stop();
        setTimeLeft(seconds);
    }, [stop, initialSeconds]);

    useEffect(() => {
        if (isRunning && timeLeft > 0) {
            intervalRef.current = setInterval(() => {
                setTimeLeft((prev) => {
                    if (prev <= 1) {
                        setIsRunning(false);
                        if (onExpireRef.current) {
                            onExpireRef.current();
                        }
                        return 0;
                    }
                    return prev - 1;
                });
            }, 1000);
        }

        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
            }
        };
    }, [isRunning, timeLeft]);

    const percentage = (timeLeft / initialSeconds) * 100;

    return {
        timeLeft,
        isRunning,
        percentage,
        start,
        stop,
        reset,
    };
}

export function useAntiCheat(sessionId, onTabSwitch) {
    useEffect(() => {
        // Disable back button
        window.history.pushState(null, '', window.location.href);
        const handlePopState = () => {
            window.history.pushState(null, '', window.location.href);
        };
        window.addEventListener('popstate', handlePopState);

        // Detect tab/window visibility change
        const handleVisibilityChange = () => {
            if (document.hidden && sessionId && onTabSwitch) {
                onTabSwitch();
            }
        };
        document.addEventListener('visibilitychange', handleVisibilityChange);

        // Disable right-click
        const handleContextMenu = (e) => e.preventDefault();
        document.addEventListener('contextmenu', handleContextMenu);

        // Disable common shortcuts
        const handleKeyDown = (e) => {
            // Disable F12, Ctrl+Shift+I, Ctrl+U
            if (
                e.key === 'F12' ||
                (e.ctrlKey && e.shiftKey && e.key === 'I') ||
                (e.ctrlKey && e.key === 'u')
            ) {
                e.preventDefault();
            }
        };
        document.addEventListener('keydown', handleKeyDown);

        return () => {
            window.removeEventListener('popstate', handlePopState);
            document.removeEventListener('visibilitychange', handleVisibilityChange);
            document.removeEventListener('contextmenu', handleContextMenu);
            document.removeEventListener('keydown', handleKeyDown);
        };
    }, [sessionId, onTabSwitch]);
}
