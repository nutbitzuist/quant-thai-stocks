'use client';

import { Log } from '@/types/dashboard';
import { S } from '../styles';

interface StatusLogsProps {
    logs: Log[];
    onClear?: () => void;
}

export function StatusLogs({ logs, onClear }: StatusLogsProps) {
    const getLogColor = (type: Log['type']) => {
        switch (type) {
            case 'success': return '#22c55e';
            case 'error': return '#ef4444';
            case 'info': default: return 'var(--muted-foreground)';
        }
    };

    const getLogIcon = (type: Log['type']) => {
        switch (type) {
            case 'success': return '✓';
            case 'error': return '✗';
            case 'info': default: return 'ℹ';
        }
    };

    return (
        <div style={S.card}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                <h3 style={{ margin: 0 }}>📋 Status Logs</h3>
                {onClear && (
                    <button
                        style={{ ...S.btn('default'), fontSize: '0.75rem', padding: '4px 8px' }}
                        onClick={onClear}
                    >
                        Clear
                    </button>
                )}
            </div>

            <div style={{
                maxHeight: '300px',
                overflowY: 'auto',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.8rem',
            }}>
                {logs.length === 0 ? (
                    <div style={{ color: 'var(--muted-foreground)', padding: '10px' }}>
                        No logs yet. Run a model to see activity.
                    </div>
                ) : (
                    logs.map((log, i) => (
                        <div
                            key={i}
                            style={{
                                display: 'flex',
                                gap: '10px',
                                padding: '6px 0',
                                borderBottom: '1px solid var(--border)',
                            }}
                        >
                            <span style={{ color: 'var(--muted-foreground)', flexShrink: 0 }}>
                                {log.time}
                            </span>
                            <span style={{
                                color: getLogColor(log.type),
                                fontWeight: '600',
                                flexShrink: 0,
                            }}>
                                {getLogIcon(log.type)}
                            </span>
                            <span style={{ color: getLogColor(log.type) }}>
                                {log.message}
                            </span>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}

export default StatusLogs;
