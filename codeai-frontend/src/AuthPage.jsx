import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const AuthPage = ({ onAuthSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const API_BASE_URL = 'http://localhost:5000/api';

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
    setSuccess('');
  };

const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    const endpoint = isLogin ? '/login' : '/register';
    const payload = isLogin 
      ? { username: formData.email, password: formData.password }  // Backend uses 'username'
      : { username: formData.email, password: formData.password, role: 'user' };

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (response.ok && data.success) {
        const successMsg = isLogin ? 'Login successful!' : 'Account created successfully!';
        setSuccess(successMsg);
        
        if (onAuthSuccess) {
          onAuthSuccess({
            username: formData.email,
            role: data.role || 'user'
          });
        }

        // Redirect to dashboard after successful auth
        setTimeout(() => {
          navigate('/dashboard');
        }, 1000);
      } else {
        if (data.errors) {
          setError(data.errors.join(', '));
        } else if (data.error) {
          setError(data.error);
        } else {
          setError('An error occurred. Please try again.');
        }
      }
    } catch (err) {
      console.error('Auth error:', err);
      setError('Failed to connect to server. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setError('');
    setSuccess('');
    setFormData({ name: '', email: '', password: '' });
  };

  return (
    <div style={styles.container}>
      <div style={styles.authCard}>
        <h2 style={styles.title}>
          {isLogin ? 'Welcome Back' : 'Create Account'}
        </h2>
        <p style={styles.subtitle}>
          {isLogin ? 'Sign in to analyze your code' : 'Start analyzing your code today'}
        </p>

        {error && (
          <div style={styles.errorBox}>
            {error}
          </div>
        )}

        {success && (
          <div style={styles.successBox}>
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} style={styles.form}>
          {!isLogin && (
            <input
              type="text"
              name="name"
              placeholder="Full name"
              value={formData.name}
              onChange={handleInputChange}
              style={styles.input}
              required
            />
          )}

          <input
            type="email"
            name="email"
            placeholder="Email address"
            value={formData.email}
            onChange={handleInputChange}
            style={styles.input}
            required
          />

          <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleInputChange}
            style={styles.input}
            required
          />

          <button 
            type="submit" 
            style={styles.submitButton}
            disabled={loading}
          >
            {loading 
              ? (isLogin ? 'Signing in...' : 'Creating account...') 
              : (isLogin ? 'Sign In' : 'Create Account')
            }
          </button>
        </form>

        <p style={styles.toggleText}>
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <span onClick={toggleMode} style={styles.toggleLink}>
            {isLogin ? 'Register here' : 'Sign in'}
          </span>
        </p>
      </div>
    </div>
  );
};

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '20px',
    paddingTop: '100px',
    backgroundColor: '#0a0a0f',
  },
  authCard: {
    width: '100%',
    maxWidth: '450px',
    padding: '48px',
    background: 'rgba(17, 17, 27, 0.8)',
    border: '1px solid rgba(139, 92, 246, 0.2)',
    borderRadius: '20px',
    backdropFilter: 'blur(20px)',
  },
  title: {
    fontSize: '32px',
    fontWeight: '700',
    marginBottom: '8px',
    textAlign: 'center',
    color: '#fff',
  },
  subtitle: {
    color: '#a1a1aa',
    textAlign: 'center',
    marginBottom: '32px',
  },
  errorBox: {
    padding: '12px 16px',
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    border: '1px solid rgba(239, 68, 68, 0.3)',
    borderRadius: '8px',
    color: '#ef4444',
    marginBottom: '20px',
    fontSize: '14px',
  },
  successBox: {
    padding: '12px 16px',
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
    border: '1px solid rgba(16, 185, 129, 0.3)',
    borderRadius: '8px',
    color: '#10b981',
    marginBottom: '20px',
    fontSize: '14px',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  input: {
    padding: '14px 20px',
    background: 'rgba(139, 92, 246, 0.05)',
    border: '1px solid rgba(139, 92, 246, 0.2)',
    borderRadius: '10px',
    color: '#fff',
    fontSize: '16px',
    outline: 'none',
  },
  submitButton: {
    padding: '14px',
    background: 'linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)',
    border: 'none',
    borderRadius: '10px',
    color: '#fff',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
    marginTop: '8px',
  },
  toggleText: {
    textAlign: 'center',
    marginTop: '24px',
    color: '#a1a1aa',
  },
  toggleLink: {
    color: '#8b5cf6',
    cursor: 'pointer',
    fontWeight: '600',
  },
};

export default AuthPage;