'use client';

import { useState, useEffect } from 'react';
import { useUser } from '@clerk/nextjs';
import Link from 'next/link';

// Admin emails (can be moved to env var later)
const ADMIN_EMAILS = [
    'email.nutty@gmail.com',
    ...(process.env.NEXT_PUBLIC_ADMIN_EMAILS || '').split(',').map(e => e.trim()).filter(Boolean)
];

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
    const { user, isLoaded } = useUser();
    const [isAdmin, setIsAdmin] = useState<boolean>(false);

    useEffect(() => {
        if (isLoaded && user) {
            const email = user.primaryEmailAddress?.emailAddress;
            if (email && ADMIN_EMAILS.includes(email)) {
                setIsAdmin(true);
            } else {
                setIsAdmin(false);
            }
        }
    }, [isLoaded, user]);

    if (!isLoaded) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-gray-50">
                <div className="text-xl font-semibold">Loading...</div>
            </div>
        );
    }

    if (!isAdmin) {
        return (
            <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 p-4 text-center">
                <h1 className="mb-4 text-3xl font-bold text-red-600">Access Denied</h1>
                <p className="mb-6 text-xl text-gray-700">You do not have permission to view the admin dashboard.</p>
                <div className="text-sm text-gray-500 mb-8">
                    User: {user?.primaryEmailAddress?.emailAddress || 'Not signed in'}
                </div>
                <Link href="/" className="rounded-md bg-blue-600 px-6 py-2 text-white hover:bg-blue-700">
                    Return to Home
                </Link>
            </div>
        );
    }

    return (
        <div style={{
            minHeight: '100vh',
            background: '#f9fafb',
            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
        }}>
            {/* Admin Header */}
            <div style={{ background: '#1f2937', color: 'white', padding: '1rem 2rem' }}>
                <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <h1 style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>QuantStack Admin</h1>
                        <span style={{
                            background: '#374151',
                            padding: '0.25rem 0.75rem',
                            borderRadius: '9999px',
                            fontSize: '0.75rem'
                        }}>
                            v2.0.2
                        </span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <div style={{ fontSize: '0.875rem', color: '#9ca3af' }}>
                            {user?.primaryEmailAddress?.emailAddress}
                        </div>
                        <Link href="/" style={{ fontSize: '0.875rem', color: '#e5e7eb', textDecoration: 'none' }}>
                            Back to App
                        </Link>
                    </div>
                </div>
            </div>

            {/* Dashboard Content */}
            <div style={{ maxWidth: '1200px', margin: '2rem auto', padding: '0 2rem' }}>
                {/* Stats Cards */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
                    <StatsCard title="Total Users" value="1,248" change="+12% this month" color="blue" />
                    <StatsCard title="Active Scans Today" value="452" change="+5% from yesterday" color="green" />
                    <StatsCard title="API Error Rate" value="0.8%" change="-0.2% improvement" color="indigo" />
                    <StatsCard title="Revenue (MRR)" value="$3,850" change="+8% this month" color="purple" />
                </div>

                {/* Main Content Area */}
                <div style={{ background: 'white', borderRadius: '0.5rem', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)', overflow: 'hidden' }}>

                    {/* Tabs */}
                    <div style={{ borderBottom: '1px solid #e5e7eb', display: 'flex' }}>
                        <TabButton
                            active={activeTab === 'users'}
                            onClick={() => setActiveTab('users')}
                            label="User Management"
                        />
                        <TabButton
                            active={activeTab === 'usage'}
                            onClick={() => setActiveTab('usage')}
                            label="Recent Usage"
                        />
                        <TabButton
                            active={activeTab === 'analytics'}
                            onClick={() => setActiveTab('analytics')}
                            label="Model Analytics"
                        />
                    </div>

                    {/* Tab Content */}
                    <div style={{ padding: '2rem' }}>
                        {activeTab === 'users' && (
                            <div>
                                <h3 style={{ fontSize: '1.125rem', fontWeight: 'bold', marginBottom: '1.5rem' }}>Registered Users</h3>
                                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                    <thead>
                                        <tr style={{ textAlign: 'left', borderBottom: '2px solid #f3f4f6' }}>
                                            <th style={{ padding: '0.75rem', fontSize: '0.875rem', color: '#6b7280' }}>Email</th>
                                            <th style={{ padding: '0.75rem', fontSize: '0.875rem', color: '#6b7280' }}>Plan</th>
                                            <th style={{ padding: '0.75rem', fontSize: '0.875rem', color: '#6b7280' }}>Status</th>
                                            <th style={{ padding: '0.75rem', fontSize: '0.875rem', color: '#6b7280' }}>Scans Used</th>
                                            <th style={{ padding: '0.75rem', fontSize: '0.875rem', color: '#6b7280' }}>Joined At</th>
                                            <th style={{ padding: '0.75rem', fontSize: '0.875rem', color: '#6b7280' }}>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {MOCK_USERS.map((user) => (
                                            <tr key={user.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                                                <td style={{ padding: '0.75rem' }}>
                                                    <div>{user.email}</div>
                                                    <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>ID: {user.id}</div>
                                                </td>
                                                <td style={{ padding: '0.75rem' }}>
                                                    <span style={{
                                                        background: user.plan === 'Unlimited' ? '#eef2ff' : '#f3f4f6',
                                                        color: user.plan === 'Unlimited' ? '#4f46e5' : '#374151',
                                                        padding: '0.25rem 0.5rem',
                                                        borderRadius: '0.25rem',
                                                        fontSize: '0.875rem'
                                                    }}>
                                                        {user.plan} ({user.billing})
                                                    </span>
                                                </td>
                                                <td style={{ padding: '0.75rem' }}>
                                                    <span style={{
                                                        background: user.status === 'Active' ? '#ecfdf5' : '#fef2f2',
                                                        color: user.status === 'Active' ? '#059669' : '#dc2626',
                                                        padding: '0.25rem 0.5rem',
                                                        borderRadius: '9999px',
                                                        fontSize: '0.75rem'
                                                    }}>
                                                        {user.status}
                                                    </span>
                                                </td>
                                                <td style={{ padding: '0.75rem', fontSize: '0.875rem' }}>
                                                    {user.scansUsed} / {user.scansLimit || '∞'}
                                                </td>
                                                <td style={{ padding: '0.75rem', fontSize: '0.875rem', color: '#6b7280' }}>{user.joinedAt}</td>
                                                <td style={{ padding: '0.75rem' }}>
                                                    <button style={{ color: '#2563eb', fontSize: '0.875rem', marginRight: '1rem' }}>Edit</button>
                                                    <button style={{ color: '#dc2626', fontSize: '0.875rem' }}>Ban</button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}

                        {activeTab === 'usage' && (
                            <div>
                                <h3 style={{ fontSize: '1.125rem', fontWeight: 'bold', marginBottom: '1.5rem' }}>Recent Scan Activity</h3>
                                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                    <thead>
                                        <tr style={{ textAlign: 'left', borderBottom: '2px solid #f3f4f6' }}>
                                            <th style={{ padding: '0.75rem', fontSize: '0.875rem', color: '#6b7280' }}>Timestamp</th>
                                            <th style={{ padding: '0.75rem', fontSize: '0.875rem', color: '#6b7280' }}>User</th>
                                            <th style={{ padding: '0.75rem', fontSize: '0.875rem', color: '#6b7280' }}>Model</th>
                                            <th style={{ padding: '0.75rem', fontSize: '0.875rem', color: '#6b7280' }}>Market</th>
                                            <th style={{ padding: '0.75rem', fontSize: '0.875rem', color: '#6b7280' }}>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {MOCK_USAGE_LOGS.map((log) => (
                                            <tr key={log.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                                                <td style={{ padding: '0.75rem', fontSize: '0.875rem', color: '#6b7280' }}>{log.timestamp}</td>
                                                <td style={{ padding: '0.75rem', fontSize: '0.875rem' }}>{log.userEmail}</td>
                                                <td style={{ padding: '0.75rem', fontSize: '0.875rem' }}>{log.model}</td>
                                                <td style={{ padding: '0.75rem', fontSize: '0.875rem' }}>{log.market}</td>
                                                <td style={{ padding: '0.75rem' }}>
                                                    <span style={{
                                                        color: log.status === 'Success' ? '#059669' : '#dc2626',
                                                        fontSize: '0.875rem'
                                                    }}>
                                                        {log.status}
                                                    </span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}

                        {activeTab === 'analytics' && (
                            <div>
                                <h3 style={{ fontSize: '1.125rem', fontWeight: 'bold', marginBottom: '1.5rem' }}>Popular Models</h3>
                                <div style={{ display: 'grid', gap: '1rem' }}>
                                    {MODEL_STATS.map((stat, idx) => (
                                        <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                            <div style={{ width: '150px', fontSize: '0.875rem' }}>{stat.model}</div>
                                            <div style={{ flex: 1, height: '24px', background: '#f3f4f6', borderRadius: '4px', overflow: 'hidden' }}>
                                                <div style={{
                                                    width: `${stat.percentage}%`,
                                                    height: '100%',
                                                    background: idx < 3 ? '#2563eb' : '#93c5fd',
                                                    transition: 'width 0.5s ease'
                                                }} />
                                            </div>
                                            <div style={{ width: '100px', fontSize: '0.875rem', color: '#6b7280' }}>
                                                {stat.count} runs ({stat.percentage}%)
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

// Helper Components
function StatsCard({ title, value, change, color }: { title: string, value: string, change: string, color: string }) {
    const colorMap: { [key: string]: string } = {
        blue: '#2563eb',
        green: '#059669',
        indigo: '#4f46e5',
        purple: '#7c3aed'
    };

    return (
        <div style={{ background: 'white', padding: '1.5rem', borderRadius: '0.5rem', boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)' }}>
            <div style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '0.5rem' }}>{title}</div>
            <div style={{ fontSize: '1.875rem', fontWeight: 'bold', color: '#111827', marginBottom: '0.25rem' }}>{value}</div>
            <div style={{ fontSize: '0.75rem', color: colorMap[color] }}>{change}</div>
        </div>
    );
}

function TabButton({ active, onClick, label }: { active: boolean, onClick: () => void, label: string }) {
    return (
        <button
            onClick={onClick}
            style={{
                padding: '1rem 1.5rem',
                fontSize: '0.875rem',
                fontWeight: 500,
                color: active ? '#2563eb' : '#6b7280',
                borderBottom: active ? '2px solid #2563eb' : '2px solid transparent',
                background: 'none',
                cursor: 'pointer',
                transition: 'all 0.2s'
            }}
        >
            {label}
        </button>
    );
}
