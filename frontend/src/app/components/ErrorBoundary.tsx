'use client';

import React from 'react';

interface ErrorBoundaryProps {
    children: React.ReactNode;
    fallback?: React.ReactNode;
}

interface ErrorBoundaryState {
    hasError: boolean;
    error: Error | null;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
    constructor(props: ErrorBoundaryProps) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error: Error): ErrorBoundaryState {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        console.error('ErrorBoundary caught an error:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <div style={{
                    minHeight: '100vh',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: '2rem',
                    background: 'var(--background)',
                    color: 'var(--foreground)',
                }}>
                    <div style={{
                        background: 'var(--card)',
                        border: '3px solid var(--destructive)',
                        boxShadow: '6px 6px 0 var(--border)',
                        padding: '2rem',
                        maxWidth: '500px',
                        textAlign: 'center',
                    }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚠️</div>
                        <h2 style={{
                            fontSize: '1.5rem',
                            fontWeight: '800',
                            marginBottom: '1rem',
                            color: 'var(--destructive)',
                        }}>
                            Something went wrong
                        </h2>
                        <p style={{
                            color: 'var(--muted-foreground)',
                            marginBottom: '1.5rem',
                            fontSize: '0.9rem',
                        }}>
                            An unexpected error occurred. Please try refreshing the page.
                        </p>
                        {this.state.error && (
                            <details style={{
                                marginBottom: '1.5rem',
                                textAlign: 'left',
                                background: 'var(--muted)',
                                padding: '1rem',
                                border: '2px solid var(--border)',
                            }}>
                                <summary style={{
                                    cursor: 'pointer',
                                    fontWeight: '600',
                                    marginBottom: '0.5rem',
                                }}>
                                    Error Details
                                </summary>
                                <pre style={{
                                    fontSize: '0.75rem',
                                    overflow: 'auto',
                                    whiteSpace: 'pre-wrap',
                                    wordBreak: 'break-word',
                                }}>
                                    {this.state.error.message}
                                </pre>
                            </details>
                        )}
                        <button
                            onClick={() => window.location.reload()}
                            style={{
                                padding: '0.75rem 1.5rem',
                                background: 'var(--primary)',
                                color: 'var(--primary-foreground)',
                                border: '3px solid var(--border)',
                                boxShadow: '4px 4px 0 var(--border)',
                                fontWeight: '700',
                                cursor: 'pointer',
                                fontSize: '0.9rem',
                            }}
                        >
                            Refresh Page
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
