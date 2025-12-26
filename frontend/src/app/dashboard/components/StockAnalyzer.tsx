'use client';

import { useState } from 'react';
import { AnalysisData, AnalysisCheckpoint, API_URL } from '@/types/dashboard';
import { S } from '../styles';

export function StockAnalyzer() {
    const [ticker, setTicker] = useState('');
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<AnalysisData | null>(null);
    const [error, setError] = useState<string | null>(null);

    const analyze = async () => {
        if (!ticker) return;
        setLoading(true);
        setError(null);
        setData(null);
        try {
            const r = await fetch(`${API_URL}/api/analysis/${ticker}`);
            if (r.ok) {
                const d: AnalysisData = await r.json();
                setData(d);
            } else {
                const e = await r.json();
                setError(e.detail || 'Failed to fetch analysis');
            }
        } catch (err: unknown) {
            if (err instanceof Error) {
                setError(err.message);
            } else {
                setError('Connection error');
            }
        }
        setLoading(false);
    };

    const downloadPdf = () => {
        if (!data) return;
        window.open(`${API_URL}/api/analysis/${data.ticker}/pdf`, '_blank');
    };

    const getScoreColor = (score: number) => {
        if (score >= 80) return '#22c55e';
        if (score >= 60) return '#3b82f6';
        if (score >= 40) return '#f59e0b';
        return '#ef4444';
    };

    return (
        <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
            <div style={S.card}>
                <h2 style={{ marginTop: 0 }}>🔍 Stock Analyzer</h2>
                <p style={{ color: 'var(--muted-foreground)' }}>
                    Get a comprehensive automated analysis of any stock (US or Thai).
                </p>

                <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
                    <input
                        style={{ ...S.input, marginBottom: 0, flex: 1, fontSize: '1.2rem', padding: '10px' }}
                        placeholder="Enter Ticker (e.g., AAPL, DELTA.BK)"
                        value={ticker}
                        onChange={e => setTicker(e.target.value.toUpperCase())}
                        onKeyDown={e => e.key === 'Enter' && analyze()}
                    />
                    <button
                        style={{ ...S.btn('primary'), fontSize: '1.2rem', padding: '10px 20px' }}
                        onClick={analyze}
                        disabled={loading}
                    >
                        {loading ? 'Analyzing...' : 'Analyze'}
                    </button>
                </div>

                {error && (
                    <div style={{
                        padding: '15px',
                        background: 'rgba(239, 68, 68, 0.1)',
                        color: '#ef4444',
                        borderRadius: 'var(--radius)',
                        marginBottom: '20px'
                    }}>
                        ⚠️ {error}
                    </div>
                )}

                {data && (
                    <div>
                        {/* Header: Name, Price, Score */}
                        <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            marginBottom: '30px',
                            flexWrap: 'wrap',
                            gap: '20px'
                        }}>
                            <div>
                                <h1 style={{ margin: 0, fontSize: '2.5rem' }}>{data.ticker}</h1>
                                <div style={{ color: 'var(--muted-foreground)', fontSize: '1.2rem' }}>{data.name}</div>
                                <div style={{ fontSize: '2rem', fontWeight: 'bold', marginTop: '10px' }}>
                                    {data.price.toLocaleString()} <span style={{ fontSize: '1rem', color: 'var(--muted-foreground)' }}>{data.currency}</span>
                                </div>
                            </div>

                            {/* Score Gauge */}
                            <ScoreGauge score={data.score} getScoreColor={getScoreColor} />

                            <div style={{ textAlign: 'right' }}>
                                <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: getScoreColor(data.score) }}>
                                    {data.recommendation}
                                </div>
                                <div style={{ maxWidth: '300px', fontSize: '0.9rem', color: 'var(--muted-foreground)', marginTop: '5px' }}>
                                    {data.summary}
                                </div>
                                <button onClick={downloadPdf} style={{ ...S.btn('primary'), marginTop: '10px' }}>
                                    ⬇️ DOWNLOAD PDF
                                </button>
                            </div>
                        </div>

                        {/* Checkpoints */}
                        <CheckpointGrid checkpoints={data.checkpoints} />

                        {/* Fundamentals & Technicals */}
                        <MetricsGrid data={data} />
                    </div>
                )}
            </div>
        </div>
    );
}

// Sub-components
function ScoreGauge({ score, getScoreColor }: { score: number; getScoreColor: (s: number) => string }) {
    return (
        <div style={{
            textAlign: 'center',
            position: 'relative',
            width: '150px',
            height: '150px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'var(--muted)',
            borderRadius: '50%'
        }}>
            <div style={{
                position: 'absolute',
                width: '130px',
                height: '130px',
                borderRadius: '50%',
                border: `10px solid ${getScoreColor(score)}`,
                borderTopColor: 'transparent',
                transform: 'rotate(-45deg)',
                transition: 'all 1s ease'
            }} />
            <div style={{ zIndex: 10, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <div style={{ fontSize: '3rem', fontWeight: 'bold', color: getScoreColor(score), lineHeight: 1 }}>{score}</div>
                <div style={{ fontSize: '0.8rem', fontWeight: 'bold', textTransform: 'uppercase' }}>Quant Score</div>
            </div>
        </div>
    );
}

function CheckpointGrid({ checkpoints }: { checkpoints: AnalysisCheckpoint[] }) {
    return (
        <>
            <h3 style={{ borderBottom: '1px solid var(--border)', paddingBottom: '10px' }}>✅ Analysis Checkpoints</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '15px', marginBottom: '30px' }}>
                {checkpoints.map((cp, i) => (
                    <div key={i} style={{
                        padding: '12px',
                        borderRadius: 'var(--radius)',
                        background: 'var(--muted)',
                        borderLeft: `5px solid ${cp.status === 'pass' ? '#22c55e' : cp.status === 'fail' ? '#ef4444' : '#f59e0b'}`
                    }}>
                        <div style={{ fontSize: '0.9rem', fontWeight: 'bold' }}>{cp.label}</div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '5px' }}>
                            <span style={{ fontSize: '0.8rem', color: 'var(--muted-foreground)' }}>Status</span>
                            <span style={{ fontWeight: 'bold', color: cp.status === 'pass' ? '#22c55e' : cp.status === 'fail' ? '#ef4444' : '#f59e0b' }}>
                                {cp.value}
                            </span>
                        </div>
                    </div>
                ))}
            </div>
        </>
    );
}

function MetricsGrid({ data }: { data: AnalysisData }) {
    return (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div>
                <h3 style={{ borderBottom: '1px solid var(--border)', paddingBottom: '10px' }}>💰 Key Fundamentals</h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                    <table style={{ width: '100%', fontSize: '0.9rem', borderCollapse: 'collapse' }}>
                        <thead><tr><th colSpan={2} style={{ textAlign: 'left', paddingBottom: '5px', color: 'var(--primary)' }}>Valuation & Growth</th></tr></thead>
                        <tbody>
                            <MetricRow label="Market Cap" value={data.metrics.market_cap ? (data.metrics.market_cap / 1e9).toFixed(2) + 'B' : '-'} />
                            <MetricRow label="P/E Ratio" value={data.metrics.pe_ratio?.toFixed(2) || '-'} />
                            <MetricRow label="Forward P/E" value={data.metrics.forward_pe?.toFixed(2) || '-'} />
                            <MetricRow label="PEG Ratio" value={data.metrics.peg_ratio?.toFixed(2) || '-'} />
                            <MetricRow label="Rev. Growth" value={data.metrics.revenue_growth ? (data.metrics.revenue_growth * 100).toFixed(2) + '%' : '-'} />
                        </tbody>
                    </table>

                    <table style={{ width: '100%', fontSize: '0.9rem', borderCollapse: 'collapse' }}>
                        <thead><tr><th colSpan={2} style={{ textAlign: 'left', paddingBottom: '5px', color: 'var(--primary)' }}>Financial Health</th></tr></thead>
                        <tbody>
                            <MetricRow label="Total Debt" value={data.metrics.total_debt ? (data.metrics.total_debt / 1e9).toFixed(2) + 'B' : '-'} />
                            <MetricRow label="Debt/Equity" value={data.metrics.debt_to_equity?.toFixed(2) || '-'} />
                            <MetricRow label="Current Ratio" value={data.metrics.current_ratio?.toFixed(2) || '-'} />
                            <MetricRow label="Free Cash Flow" value={data.metrics.free_cash_flow ? (data.metrics.free_cash_flow / 1e9).toFixed(2) + 'B' : '-'} />
                        </tbody>
                    </table>
                </div>
            </div>

            <div>
                <h3 style={{ borderBottom: '1px solid var(--border)', paddingBottom: '10px' }}>📈 Technical Indicators</h3>
                <table style={{ width: '100%', fontSize: '0.9rem', borderCollapse: 'collapse' }}>
                    <tbody>
                        <MetricRow label="RSI (14)" value={data.technicals.rsi?.toFixed(2) || '-'} padding="8px 0" />
                        <MetricRow label="MACD" value={data.technicals.macd?.toFixed(2) || '-'} padding="8px 0" />
                        <MetricRow label="SMA 200" value={data.technicals.sma_200?.toFixed(2) || '-'} padding="8px 0" />
                        <tr>
                            <td style={{ padding: '8px 0', color: 'var(--muted-foreground)' }}>1Y Return</td>
                            <td style={{
                                textAlign: 'right',
                                fontWeight: 'bold',
                                color: (data.technicals.return_1y || 0) >= 0 ? '#22c55e' : '#ef4444'
                            }}>
                                {data.technicals.return_1y?.toFixed(2)}%
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    );
}

function MetricRow({ label, value, padding = '4px 0' }: { label: string; value: string; padding?: string }) {
    return (
        <tr>
            <td style={{ padding, color: 'var(--muted-foreground)' }}>{label}</td>
            <td style={{ textAlign: 'right', fontWeight: 'bold' }}>{value}</td>
        </tr>
    );
}

export default StockAnalyzer;
