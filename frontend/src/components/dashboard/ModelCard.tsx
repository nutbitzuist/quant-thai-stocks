
import { useState } from 'react';
import { Model, ModelResult } from '@/types/dashboard';
import { S } from '@/styles/dashboard';

interface ModelCardProps {
    model: Model;
    result?: ModelResult;
    running: boolean;
    onRun: () => void;
    onPDF: (id: string) => void;
    onEnhancedPDF: (modelId: string) => void;
    onRunWithParams?: (params: Record<string, any>) => void;
}

export default function ModelCard({
    model,
    result,
    running,
    onRun,
    onPDF,
    onEnhancedPDF,
    onRunWithParams
}: ModelCardProps) {
    const [showParams, setShowParams] = useState(false);
    const [customParams, setCustomParams] = useState<Record<string, any>>(model.default_parameters || {});

    const handleParamChange = (key: string, value: any) => {
        setCustomParams(prev => ({ ...prev, [key]: value }));
    };

    const runWithCustomParams = () => {
        if (onRunWithParams) {
            onRunWithParams(customParams);
        }
        setShowParams(false);
    };

    const getCategoryColor = () => {
        if (model.category === 'Technical') return { bg: 'var(--accent)', color: 'var(--accent-foreground)' };
        if (model.category === 'Quantitative') return { bg: '#8b5cf6', color: 'white' };
        return { bg: 'var(--muted)', color: 'var(--muted-foreground)' };
    };

    const catStyle = getCategoryColor();

    return (
        <div style={S.card}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                    <h3 style={{ margin: 0, fontFamily: 'var(--font-sans)', fontWeight: '700' }}>{model.name}</h3>
                    <span style={{ fontSize: '11px', padding: '3px 8px', borderRadius: '0', background: catStyle.bg, color: catStyle.color, border: '2px solid var(--border)', fontWeight: '700', textTransform: 'uppercase' as const, display: 'inline-block', marginTop: '6px' }}>{model.category}</span>
                </div>
                <div style={{ display: 'flex', gap: '5px' }}>
                    <button style={{ ...S.button.secondary, fontSize: '11px', padding: '4px 8px' }} onClick={() => setShowParams(!showParams)} title="Customize Parameters">⚙️</button>
                    <button style={{ ...S.button.primary, opacity: running ? 0.6 : 1 }} onClick={onRun} disabled={running}>{running ? '⏳...' : '▶ Run'}</button>
                </div>
            </div>
            <p style={{ color: 'var(--muted-foreground)', fontSize: '12px', margin: '10px 0' }}>{model.description}</p>

            {/* Parameter Customization Panel */}
            {showParams && model.default_parameters && (
                <div style={{ background: 'var(--muted)', padding: '16px', borderRadius: '0', marginBottom: '12px', border: '3px solid var(--border)', boxShadow: '4px 4px 0 var(--border)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', borderBottom: '2px solid var(--border)', paddingBottom: '10px' }}>
                        <h4 style={{ margin: 0, fontSize: '14px', fontWeight: '700', fontFamily: 'var(--font-sans)', textTransform: 'uppercase' as const }}>⚙️ Custom Parameters</h4>
                        <button style={{ background: 'var(--card)', border: '2px solid var(--border)', cursor: 'pointer', fontSize: '14px', padding: '4px 8px', fontWeight: '700', boxShadow: '2px 2px 0 var(--border)' }} onClick={() => setShowParams(false)}>✕</button>
                    </div>
                    <div style={{ display: 'grid', gap: '8px' }}>
                        {Object.entries(model.default_parameters).map(([key, defaultValue]) => (
                            <div key={key} style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                <label style={{ fontSize: '11px', minWidth: '120px', color: 'var(--foreground)' }}>{key.replace(/_/g, ' ')}</label>
                                {typeof defaultValue === 'boolean' ? (
                                    <input
                                        type="checkbox"
                                        checked={customParams[key] ?? defaultValue}
                                        onChange={(e) => handleParamChange(key, e.target.checked)}
                                    />
                                ) : typeof defaultValue === 'number' ? (
                                    <input
                                        type="number"
                                        style={{ ...S.input, width: '80px', marginBottom: 0, padding: '4px 8px' }}
                                        value={customParams[key] ?? defaultValue}
                                        onChange={(e) => handleParamChange(key, parseFloat(e.target.value) || 0)}
                                        step={defaultValue < 1 ? 0.1 : 1}
                                    />
                                ) : (
                                    <input
                                        type="text"
                                        style={{ ...S.input, width: '100px', marginBottom: 0, padding: '4px 8px' }}
                                        value={customParams[key] ?? defaultValue}
                                        onChange={(e) => handleParamChange(key, e.target.value)}
                                    />
                                )}
                            </div>
                        ))}
                    </div>
                    <div style={{ marginTop: '10px', display: 'flex', gap: '8px' }}>
                        <button style={{ ...S.button.success, fontSize: '11px', padding: '6px 12px' }} onClick={runWithCustomParams} disabled={running}>
                            {running ? '⏳...' : '▶ Run with Custom'}
                        </button>
                        <button style={{ ...S.button.secondary, fontSize: '11px', padding: '6px 12px' }} onClick={() => setCustomParams(model.default_parameters || {})}>
                            Reset
                        </button>
                    </div>
                </div>
            )}

            {result && (
                <div style={{ borderTop: '1px solid var(--border)', paddingTop: '10px' }}>
                    <div style={{ display: 'flex', gap: '10px', marginBottom: '8px', fontSize: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
                        <span style={{ color: '#22c55e' }}>✅ {result.buy_signals.length} Buy</span>
                        <span style={{ color: 'var(--destructive)' }}>🔻 {result.sell_signals.length} Sell</span>
                        <span style={{ color: 'var(--muted-foreground)' }}>{result.stocks_with_data}/{result.total_stocks_analyzed} stocks</span>
                        {result.data_coverage_pct !== undefined && result.data_coverage_pct < 0.8 && (
                            <span style={{ color: '#f59e0b', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '4px', background: '#fffbeb', padding: '2px 6px', borderRadius: '4px', border: '1px solid #fcd34d' }}>
                                ⚠️ Low Data ({(result.data_coverage_pct * 100).toFixed(0)}%)
                            </span>
                        )}
                        <span style={{ color: 'var(--muted-foreground)', fontSize: '11px', fontStyle: 'italic' }}>(Top signals shown)</span>
                    </div>
                    {result.buy_signals.slice(0, 4).map((s, i) => (
                        <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', padding: '3px 0' }}>
                            <b>{s.ticker.replace('.BK', '')}</b><span>${s.price_at_signal.toFixed(2)}</span><span style={{ color: '#22c55e' }}>{s.score.toFixed(0)}</span>
                        </div>
                    ))}
                    <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
                        <button style={{ ...S.button.secondary, fontSize: '11px' }} onClick={() => onPDF(result.run_id)}>📄 PDF</button>
                        <button style={{ ...S.button.primary, fontSize: '11px' }} onClick={() => onEnhancedPDF(model.id)}>📊 Enhanced PDF</button>
                    </div>
                </div>
            )}
        </div>
    );
}
