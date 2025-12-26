'use client';

import { Model, ModelResult } from '@/types/dashboard';
import { S } from '../styles';

interface ModelCardProps {
    model: Model;
    result?: ModelResult;
    running: boolean;
    onRun: (id: string) => void;
}

export function ModelCard({ model, result, running, onRun }: ModelCardProps) {
    const getCategoryColor = (category: string) => {
        switch (category) {
            case 'technical': return '#3b82f6';
            case 'fundamental': return '#22c55e';
            case 'quantitative': return '#a855f7';
            default: return 'var(--muted-foreground)';
        }
    };

    const getCategoryIcon = (category: string) => {
        switch (category) {
            case 'technical': return '📈';
            case 'fundamental': return '📊';
            case 'quantitative': return '🔢';
            default: return '📋';
        }
    };

    return (
        <div style={{
            ...S.card,
            display: 'flex',
            flexDirection: 'column',
            height: '100%',
        }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', marginBottom: '10px' }}>
                <span style={{ fontSize: '1.5rem' }}>{getCategoryIcon(model.category)}</span>
                <div style={{ flex: 1 }}>
                    <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: '700' }}>{model.name}</h3>
                    <span style={{
                        fontSize: '0.7rem',
                        background: getCategoryColor(model.category),
                        color: '#fff',
                        padding: '2px 6px',
                        fontWeight: '600',
                        textTransform: 'uppercase',
                    }}>
                        {model.category}
                    </span>
                </div>
            </div>

            <p style={{
                color: 'var(--muted-foreground)',
                fontSize: '0.8rem',
                flex: 1,
                marginBottom: '10px',
            }}>
                {model.description}
            </p>

            {result && (
                <div style={{
                    marginBottom: '10px',
                    padding: '8px',
                    background: 'var(--muted)',
                    fontSize: '0.75rem',
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>Buy Signals:</span>
                        <strong style={{ color: '#22c55e' }}>{result.buy_signals.length}</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>Sell Signals:</span>
                        <strong style={{ color: '#ef4444' }}>{result.sell_signals.length}</strong>
                    </div>
                </div>
            )}

            <button
                style={S.btn(running ? 'default' : 'primary')}
                onClick={() => onRun(model.id)}
                disabled={running}
            >
                {running ? '⏳ Running...' : '▶️ Run'}
            </button>
        </div>
    );
}

export default ModelCard;
