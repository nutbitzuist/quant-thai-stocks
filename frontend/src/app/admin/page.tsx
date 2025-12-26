'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

// Admin emails (can be moved to env var later)
const ADMIN_EMAILS = ['email.nutty@gmail.com'];

// Mock data for users
const MOCK_USERS = [
    { id: 1, email: 'john.trader@gmail.com', plan: 'Pro', billing: 'Annual', status: 'Active', scansUsed: 87, scansLimit: 150, joinedAt: '2024-11-15' },
    { id: 2, email: 'sarah.investor@outlook.com', plan: 'Unlimited', billing: 'Monthly', status: 'Active', scansUsed: 234, scansLimit: null, joinedAt: '2024-10-22' },
    { id: 3, email: 'mike.stocks@yahoo.com', plan: 'Pro', billing: 'Monthly', status: 'Active', scansUsed: 45, scansLimit: 150, joinedAt: '2024-12-01' },
    { id: 4, email: 'lisa.quant@gmail.com', plan: 'Unlimited', billing: 'Annual', status: 'Active', scansUsed: 512, scansLimit: null, joinedAt: '2024-09-10' },
    { id: 5, email: 'david.trader@gmail.com', plan: 'Pro', billing: 'Annual', status: 'Inactive', scansUsed: 0, scansLimit: 150, joinedAt: '2024-08-05' },
];

// Mock data for usage logs
const MOCK_USAGE_LOGS = [
    { id: 1, timestamp: '2024-12-26 09:45:23', userEmail: 'sarah.investor@outlook.com', model: 'CANSLIM', stocksScanned: 100, market: 'US', status: 'Success' },
    { id: 2, timestamp: '2024-12-26 09:42:11', userEmail: 'john.trader@gmail.com', model: 'Minervini Trend', stocksScanned: 50, market: 'Thai', status: 'Success' },
    { id: 3, timestamp: '2024-12-26 09:38:45', userEmail: 'lisa.quant@gmail.com', model: 'Piotroski F-Score', stocksScanned: 100, market: 'US', status: 'Success' },
    { id: 4, timestamp: '2024-12-26 09:35:00', userEmail: 'sarah.investor@outlook.com', model: 'RSI Reversal', stocksScanned: 100, market: 'US', status: 'Success' },
    { id: 5, timestamp: '2024-12-26 09:30:12', userEmail: 'mike.stocks@yahoo.com', model: 'Magic Formula', stocksScanned: 50, market: 'Thai', status: 'Success' },
    { id: 6, timestamp: '2024-12-26 09:25:33', userEmail: 'lisa.quant@gmail.com', model: 'Value Composite', stocksScanned: 100, market: 'US', status: 'Success' },
    { id: 7, timestamp: '2024-12-26 09:20:00', userEmail: 'john.trader@gmail.com', model: 'MACD Crossover', stocksScanned: 50, market: 'Thai', status: 'Failed' },
    { id: 8, timestamp: '2024-12-26 09:15:45', userEmail: 'sarah.investor@outlook.com', model: 'Bollinger Squeeze', stocksScanned: 100, market: 'US', status: 'Success' },
    { id: 9, timestamp: '2024-12-26 09:10:22', userEmail: 'lisa.quant@gmail.com', model: 'Factor Momentum', stocksScanned: 100, market: 'US', status: 'Success' },
    { id: 10, timestamp: '2024-12-26 09:05:00', userEmail: 'mike.stocks@yahoo.com', model: 'Turtle Trading', stocksScanned: 50, market: 'Thai', status: 'Success' },
];

// Model usage stats
const MODEL_STATS = [
    { model: 'CANSLIM', count: 245, percentage: 18 },
    { model: 'Minervini Trend', count: 189, percentage: 14 },
    { model: 'Piotroski F-Score', count: 156, percentage: 12 },
    { model: 'RSI Reversal', count: 134, percentage: 10 },
    { model: 'Magic Formula', count: 112, percentage: 8 },
    { model: 'Value Composite', count: 98, percentage: 7 },
    { model: 'Other Models', count: 416, percentage: 31 },
];

export default function AdminPage() {
    const [activeTab, setActiveTab] = useState<'users' | 'usage' | 'analytics'>('users');
    const [isAdmin, setIsAdmin] = useState<boolean | null>(null);
    const [userEmail, setUserEmail] = useState<string>('');

    // Check admin status - in production, use Clerk's useUser hook
    useEffect(() => {
        // For demo purposes, auto-login as admin
        // In production, check against Clerk user email
        const checkAdmin = async () => {
            try {
                // Try to get user from Clerk
                const clerk = await import('@clerk/nextjs');
                // For now, assume admin access for demo
                setIsAdmin(true);
                setUserEmail('email.nutty@gmail.com');
            } catch {
                // Clerk not configured, allow admin access for demo
                setIsAdmin(true);
                setUserEmail('email.nutty@gmail.com');
            }
        };
        checkAdmin();
    }, []);

    if (isAdmin === null) {
        return (
            <div style={{
                minHeight: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: 'var(--background)',
            }}>
                <div style={{ fontSize: '1.5rem', fontWeight: '700' }}>Loading...</div>
            </div>
        );
    }

    if (!isAdmin) {
        return (
            <div style={{
                minHeight: '100vh',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                background: 'var(--background)',
                gap: '1rem',
            }}>
                <div style={{ fontSize: '4rem' }}>🚫</div>
                <h1 style={{ fontSize: '2rem', fontWeight: '900' }}>Access Denied</h1>
                <p style={{ color: 'var(--muted-foreground)' }}>You don't have admin privileges.</p>
                <Link href="/" style={{
                    padding: '0.75rem 1.5rem',
                    background: 'var(--primary)',
                    color: 'var(--primary-foreground)',
                    border: '3px solid var(--border)',
                    boxShadow: '4px 4px 0 var(--border)',
                    textDecoration: 'none',
                    fontWeight: '700',
                }}>
                    Return Home
                </Link>
            </div>
        );
    }

    return (
        <div style={{
            minHeight: '100vh',
            background: 'var(--background)',
            padding: '2rem',
        }}>
            <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
                {/* Header */}
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '2rem',
                    paddingBottom: '1rem',
                    borderBottom: '3px solid var(--border)',
                }}>
                    <div>
                        <h1 style={{ fontSize: '2rem', fontWeight: '900', marginBottom: '0.25rem' }}>
                            🔐 Admin Dashboard
                        </h1>
                        <p style={{ color: 'var(--muted-foreground)', fontSize: '0.9rem' }}>
                            Logged in as: {userEmail}
                        </p>
                    </div>
                    <Link href="/" style={{
                        padding: '0.5rem 1rem',
                        background: 'var(--card)',
                        border: '2px solid var(--border)',
                        boxShadow: '3px 3px 0 var(--border)',
                        textDecoration: 'none',
                        color: 'var(--foreground)',
                        fontWeight: '600',
                        fontSize: '0.9rem',
                    }}>
                        ← Back to Site
                    </Link>
                </div>

                {/* Stats Overview */}
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                    gap: '1rem',
                    marginBottom: '2rem',
                }}>
                    <StatCard icon="👥" label="Total Users" value={MOCK_USERS.length.toString()} />
                    <StatCard icon="✅" label="Active Users" value={MOCK_USERS.filter(u => u.status === 'Active').length.toString()} />
                    <StatCard icon="📊" label="Total Scans Today" value="1,350" />
                    <StatCard icon="💰" label="MRR" value="$2,847" />
                </div>

                {/* Tab Navigation */}
                <div style={{
                    display: 'flex',
                    gap: '0.5rem',
                    marginBottom: '1.5rem',
                }}>
                    {(['users', 'usage', 'analytics'] as const).map(tab => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            style={{
                                padding: '0.75rem 1.5rem',
                                background: activeTab === tab ? 'var(--primary)' : 'var(--card)',
                                color: activeTab === tab ? 'var(--primary-foreground)' : 'var(--foreground)',
                                border: '3px solid var(--border)',
                                boxShadow: activeTab === tab ? '4px 4px 0 var(--border)' : '2px 2px 0 var(--border)',
                                fontWeight: '700',
                                cursor: 'pointer',
                                textTransform: 'capitalize',
                            }}
                        >
                            {tab === 'users' && '👥 '}
                            {tab === 'usage' && '📋 '}
                            {tab === 'analytics' && '📈 '}
                            {tab}
                        </button>
                    ))}
                </div>

                {/* Tab Content */}
                <div style={{
                    background: 'var(--card)',
                    border: '3px solid var(--border)',
                    boxShadow: '5px 5px 0 var(--border)',
                    padding: '1.5rem',
                }}>
                    {activeTab === 'users' && <UsersTable users={MOCK_USERS} />}
                    {activeTab === 'usage' && <UsageLogs logs={MOCK_USAGE_LOGS} />}
                    {activeTab === 'analytics' && <Analytics stats={MODEL_STATS} />}
                </div>
            </div>
        </div>
    );
}

function StatCard({ icon, label, value }: { icon: string; label: string; value: string }) {
    return (
        <div style={{
            padding: '1.25rem',
            background: 'var(--card)',
            border: '3px solid var(--border)',
            boxShadow: '4px 4px 0 var(--border)',
        }}>
            <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>{icon}</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--muted-foreground)', marginBottom: '0.25rem' }}>{label}</div>
            <div style={{ fontSize: '1.75rem', fontWeight: '900' }}>{value}</div>
        </div>
    );
}

function UsersTable({ users }: { users: typeof MOCK_USERS }) {
    return (
        <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '800', marginBottom: '1rem' }}>
                User Management
            </h2>
            <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                        <tr style={{ borderBottom: '3px solid var(--border)' }}>
                            <th style={thStyle}>Email</th>
                            <th style={thStyle}>Plan</th>
                            <th style={thStyle}>Billing</th>
                            <th style={thStyle}>Status</th>
                            <th style={thStyle}>Scans Used</th>
                            <th style={thStyle}>Joined</th>
                            <th style={thStyle}>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {users.map(user => (
                            <tr key={user.id} style={{ borderBottom: '1px solid var(--border)' }}>
                                <td style={tdStyle}>
                                    <strong>{user.email}</strong>
                                </td>
                                <td style={tdStyle}>
                                    <span style={{
                                        padding: '0.25rem 0.5rem',
                                        background: user.plan === 'Unlimited' ? 'var(--primary)' : 'var(--muted)',
                                        color: user.plan === 'Unlimited' ? 'var(--primary-foreground)' : 'var(--foreground)',
                                        fontWeight: '600',
                                        fontSize: '0.8rem',
                                        border: '2px solid var(--border)',
                                    }}>
                                        {user.plan}
                                    </span>
                                </td>
                                <td style={tdStyle}>{user.billing}</td>
                                <td style={tdStyle}>
                                    <span style={{
                                        padding: '0.25rem 0.5rem',
                                        background: user.status === 'Active' ? 'var(--success)' : 'var(--muted)',
                                        color: user.status === 'Active' ? 'white' : 'var(--muted-foreground)',
                                        fontWeight: '600',
                                        fontSize: '0.8rem',
                                        border: '2px solid var(--border)',
                                    }}>
                                        {user.status}
                                    </span>
                                </td>
                                <td style={tdStyle}>
                                    {user.scansLimit ? (
                                        <div>
                                            <span style={{ fontWeight: '700' }}>{user.scansUsed}</span>
                                            <span style={{ color: 'var(--muted-foreground)' }}> / {user.scansLimit}</span>
                                            <div style={{
                                                height: '6px',
                                                background: 'var(--muted)',
                                                marginTop: '4px',
                                                border: '1px solid var(--border)',
                                            }}>
                                                <div style={{
                                                    height: '100%',
                                                    width: `${(user.scansUsed / user.scansLimit) * 100}%`,
                                                    background: user.scansUsed / user.scansLimit > 0.8 ? '#ef4444' : 'var(--success)',
                                                }} />
                                            </div>
                                        </div>
                                    ) : (
                                        <span style={{ color: 'var(--primary)', fontWeight: '700' }}>∞ {user.scansUsed}</span>
                                    )}
                                </td>
                                <td style={tdStyle}>{user.joinedAt}</td>
                                <td style={tdStyle}>
                                    <button style={{
                                        padding: '0.25rem 0.5rem',
                                        background: 'var(--card)',
                                        border: '2px solid var(--border)',
                                        cursor: 'pointer',
                                        fontSize: '0.8rem',
                                    }}>
                                        View
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

function UsageLogs({ logs }: { logs: typeof MOCK_USAGE_LOGS }) {
    return (
        <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '800', marginBottom: '1rem' }}>
                Usage Logs
            </h2>
            <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                        <tr style={{ borderBottom: '3px solid var(--border)' }}>
                            <th style={thStyle}>Timestamp</th>
                            <th style={thStyle}>User</th>
                            <th style={thStyle}>Model</th>
                            <th style={thStyle}>Stocks</th>
                            <th style={thStyle}>Market</th>
                            <th style={thStyle}>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {logs.map(log => (
                            <tr key={log.id} style={{ borderBottom: '1px solid var(--border)' }}>
                                <td style={tdStyle}>
                                    <span style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                                        {log.timestamp}
                                    </span>
                                </td>
                                <td style={tdStyle}>{log.userEmail}</td>
                                <td style={tdStyle}>
                                    <strong>{log.model}</strong>
                                </td>
                                <td style={tdStyle}>{log.stocksScanned}</td>
                                <td style={tdStyle}>
                                    <span style={{
                                        padding: '0.15rem 0.4rem',
                                        background: log.market === 'US' ? '#3b82f6' : '#10b981',
                                        color: 'white',
                                        fontSize: '0.75rem',
                                        fontWeight: '600',
                                    }}>
                                        {log.market}
                                    </span>
                                </td>
                                <td style={tdStyle}>
                                    <span style={{
                                        padding: '0.15rem 0.4rem',
                                        background: log.status === 'Success' ? 'var(--success)' : '#ef4444',
                                        color: 'white',
                                        fontSize: '0.75rem',
                                        fontWeight: '600',
                                    }}>
                                        {log.status}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

function Analytics({ stats }: { stats: typeof MODEL_STATS }) {
    const maxCount = Math.max(...stats.map(s => s.count));

    return (
        <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '800', marginBottom: '1rem' }}>
                Model Usage Analytics
            </h2>
            <p style={{ color: 'var(--muted-foreground)', marginBottom: '1.5rem' }}>
                Top models by usage this month
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {stats.map((stat, i) => (
                    <div key={i}>
                        <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            marginBottom: '0.25rem',
                        }}>
                            <span style={{ fontWeight: '600' }}>{stat.model}</span>
                            <span style={{ color: 'var(--muted-foreground)' }}>
                                {stat.count} scans ({stat.percentage}%)
                            </span>
                        </div>
                        <div style={{
                            height: '24px',
                            background: 'var(--muted)',
                            border: '2px solid var(--border)',
                        }}>
                            <div style={{
                                height: '100%',
                                width: `${(stat.count / maxCount) * 100}%`,
                                background: i === 0 ? 'var(--primary)' : i < 3 ? 'var(--success)' : '#64748b',
                                transition: 'width 0.5s ease',
                            }} />
                        </div>
                    </div>
                ))}
            </div>

            {/* Summary Stats */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                gap: '1rem',
                marginTop: '2rem',
                padding: '1rem',
                background: 'var(--muted)',
                border: '2px solid var(--border)',
            }}>
                <div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--muted-foreground)' }}>Total Scans</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: '900' }}>1,350</div>
                </div>
                <div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--muted-foreground)' }}>Unique Users</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: '900' }}>4</div>
                </div>
                <div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--muted-foreground)' }}>Success Rate</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: '900', color: 'var(--success)' }}>98.2%</div>
                </div>
                <div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--muted-foreground)' }}>Avg Scans/User</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: '900' }}>337</div>
                </div>
            </div>
        </div>
    );
}

const thStyle: React.CSSProperties = {
    textAlign: 'left',
    padding: '0.75rem',
    fontWeight: '700',
    fontSize: '0.85rem',
    color: 'var(--muted-foreground)',
};

const tdStyle: React.CSSProperties = {
    padding: '0.75rem',
    fontSize: '0.9rem',
};
