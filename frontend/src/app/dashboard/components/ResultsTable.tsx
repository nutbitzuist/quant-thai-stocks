'use client';

import { Signal } from '@/types/dashboard';
import { S } from '../styles';

interface ResultsTableProps {
    buySignals: Signal[];
    sellSignals: Signal[];
    modelName: string;
    showSell?: boolean;
    onDownloadPdf?: () => void;
}

export function ResultsTable({
    buySignals,
    sellSignals,
    modelName,
    showSell = true,
    onDownloadPdf
}: ResultsTableProps) {
    const totalSignals = buySignals.length + sellSignals.length;

    return (
        <div style={S.card}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                <h3 style={{ margin: 0 }}>📊 {modelName} Results</h3>
                {onDownloadPdf && (
                    <button style={S.btn('primary')} onClick={onDownloadPdf}>
                        ⬇️ PDF Report
                    </button>
                )}
            </div>

            <div style={{ display: 'flex', gap: '20px', marginBottom: '15px' }}>
                <div style={{
                    padding: '10px 15px',
                    background: 'rgba(34, 197, 94, 0.1)',
                    border: '2px solid #22c55e',
                }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#22c55e' }}>
                        {buySignals.length}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--muted-foreground)' }}>Buy Signals</div>
                </div>
                {showSell && (
                    <div style={{
                        padding: '10px 15px',
                        background: 'rgba(239, 68, 68, 0.1)',
                        border: '2px solid #ef4444',
                    }}>
                        <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#ef4444' }}>
                            {sellSignals.length}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--muted-foreground)' }}>Sell Signals</div>
                    </div>
                )}
            </div>

            {/* Buy Signals Table */}
            {buySignals.length > 0 && (
                <>
                    <h4 style={{ color: '#22c55e', marginBottom: '10px' }}>🟢 Buy Signals</h4>
                    <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '20px' }}>
                        <thead>
                            <tr>
                                <th style={tableHeaderStyle}>Ticker</th>
                                <th style={tableHeaderStyle}>Score</th>
                                <th style={tableHeaderStyle}>Price</th>
                                <th style={tableHeaderStyle}>Signal</th>
                            </tr>
                        </thead>
                        <tbody>
                            {buySignals.map((signal, i) => (
                                <tr key={i} style={{ background: i % 2 === 0 ? 'var(--muted)' : 'transparent' }}>
                                    <td style={tableCellStyle}><strong>{signal.ticker}</strong></td>
                                    <td style={tableCellStyle}>{signal.score.toFixed(2)}</td>
                                    <td style={tableCellStyle}>${signal.price_at_signal.toFixed(2)}</td>
                                    <td style={{ ...tableCellStyle, color: '#22c55e' }}>{signal.signal_type}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </>
            )}

            {/* Sell Signals Table */}
            {showSell && sellSignals.length > 0 && (
                <>
                    <h4 style={{ color: '#ef4444', marginBottom: '10px' }}>🔴 Sell Signals</h4>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr>
                                <th style={tableHeaderStyle}>Ticker</th>
                                <th style={tableHeaderStyle}>Score</th>
                                <th style={tableHeaderStyle}>Price</th>
                                <th style={tableHeaderStyle}>Signal</th>
                            </tr>
                        </thead>
                        <tbody>
                            {sellSignals.map((signal, i) => (
                                <tr key={i} style={{ background: i % 2 === 0 ? 'var(--muted)' : 'transparent' }}>
                                    <td style={tableCellStyle}><strong>{signal.ticker}</strong></td>
                                    <td style={tableCellStyle}>{signal.score.toFixed(2)}</td>
                                    <td style={tableCellStyle}>${signal.price_at_signal.toFixed(2)}</td>
                                    <td style={{ ...tableCellStyle, color: '#ef4444' }}>{signal.signal_type}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </>
            )}

            {totalSignals === 0 && (
                <div style={{
                    padding: '20px',
                    textAlign: 'center',
                    color: 'var(--muted-foreground)',
                    background: 'var(--muted)',
                }}>
                    No signals found for this model run.
                </div>
            )}
        </div>
    );
}

const tableHeaderStyle: React.CSSProperties = {
    textAlign: 'left',
    padding: '10px',
    borderBottom: '2px solid var(--border)',
    fontWeight: '700',
    fontSize: '0.8rem',
    textTransform: 'uppercase',
};

const tableCellStyle: React.CSSProperties = {
    padding: '8px 10px',
    borderBottom: '1px solid var(--border)',
    fontSize: '0.85rem',
};

export default ResultsTable;
