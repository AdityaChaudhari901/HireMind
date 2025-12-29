import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [admin, setAdmin] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('adminToken');
        const savedAdmin = localStorage.getItem('adminUser');

        if (token && savedAdmin) {
            setAdmin(JSON.parse(savedAdmin));
            // Verify token is still valid
            authAPI.getMe()
                .then(res => setAdmin(res.data))
                .catch(() => {
                    localStorage.removeItem('adminToken');
                    localStorage.removeItem('adminUser');
                    setAdmin(null);
                })
                .finally(() => setLoading(false));
        } else {
            setLoading(false);
        }
    }, []);

    const login = async (email, password) => {
        const response = await authAPI.adminLogin(email, password);
        const { access_token, admin } = response.data;

        localStorage.setItem('adminToken', access_token);
        localStorage.setItem('adminUser', JSON.stringify(admin));
        setAdmin(admin);

        return admin;
    };

    const logout = () => {
        localStorage.removeItem('adminToken');
        localStorage.removeItem('adminUser');
        setAdmin(null);
    };

    const register = async (data) => {
        const response = await authAPI.adminRegister(data);
        return response.data;
    };

    return (
        <AuthContext.Provider value={{ admin, loading, login, logout, register }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
