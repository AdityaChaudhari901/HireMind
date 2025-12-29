import { Loader2 } from 'lucide-react';

export function Loading({ message = 'Loading...' }) {
    return (
        <div className="flex flex-col items-center justify-center min-h-[200px]">
            <Loader2 className="w-8 h-8 text-primary-600 animate-spin" />
            <p className="mt-3 text-slate-600">{message}</p>
        </div>
    );
}

export function Button({
    children,
    variant = 'primary',
    size = 'md',
    loading = false,
    disabled = false,
    className = '',
    ...props
}) {
    const baseClass = 'btn';
    const variants = {
        primary: 'btn-primary',
        secondary: 'btn-secondary',
        success: 'btn-success',
        danger: 'btn-danger',
    };
    const sizes = {
        sm: 'btn-sm',
        md: '',
        lg: 'btn-lg',
    };

    return (
        <button
            className={`${baseClass} ${variants[variant]} ${sizes[size]} ${className}`}
            disabled={disabled || loading}
            {...props}
        >
            {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
            {children}
        </button>
    );
}

export function Input({
    label,
    error,
    className = '',
    ...props
}) {
    return (
        <div className="space-y-1">
            {label && (
                <label className="block text-sm font-medium text-slate-700">
                    {label}
                </label>
            )}
            <input
                className={`input ${error ? 'input-error' : ''} ${className}`}
                {...props}
            />
            {error && (
                <p className="text-sm text-danger-500">{error}</p>
            )}
        </div>
    );
}

export function Card({ children, className = '' }) {
    return (
        <div className={`card ${className}`}>
            {children}
        </div>
    );
}

export function CardHeader({ children, className = '' }) {
    return (
        <div className={`card-header ${className}`}>
            {children}
        </div>
    );
}

export function CardBody({ children, className = '' }) {
    return (
        <div className={`card-body ${className}`}>
            {children}
        </div>
    );
}

export function Badge({ children, variant = 'default', className = '' }) {
    const variants = {
        default: 'bg-slate-100 text-slate-700',
        primary: 'bg-primary-100 text-primary-700',
        success: 'bg-success-50 text-success-600',
        warning: 'bg-warning-50 text-warning-600',
        danger: 'bg-danger-50 text-danger-600',
    };

    return (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variants[variant]} ${className}`}>
            {children}
        </span>
    );
}

export function Select({ label, error, options = [], className = '', ...props }) {
    return (
        <div className="space-y-1">
            {label && (
                <label className="block text-sm font-medium text-slate-700">
                    {label}
                </label>
            )}
            <select
                className={`input ${error ? 'input-error' : ''} ${className}`}
                {...props}
            >
                {options.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                        {opt.label}
                    </option>
                ))}
            </select>
            {error && (
                <p className="text-sm text-danger-500">{error}</p>
            )}
        </div>
    );
}
