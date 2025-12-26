
import { Model, ModelResult } from '@/types/dashboard';
import ModelCard from './ModelCard';
import { S } from '@/styles/dashboard';

interface ModelListProps {
    models: Model[];
    modelSubTab: string;
    results: Record<string, ModelResult>;
    running: string | null;
    connected: boolean;
    onRun: (id: string) => void;
    onPDF: (id: string) => void;
    onEnhancedPDF: (modelId: string) => void;
    onRunWithParams: (modelId: string, params: Record<string, any>) => void;
}

export default function ModelList({
    models,
    modelSubTab,
    results,
    running,
    connected,
    onRun,
    onPDF,
    onEnhancedPDF,
    onRunWithParams
}: ModelListProps) {
    if (!connected) {
        return (
            <div style={{ ...S.card, background: 'var(--accent)', borderLeft: '4px solid var(--primary)', color: 'var(--accent-foreground)' }}>
                <h3 style={{ margin: '0 0 0.5rem 0' }}>⚠️ Backend Not Connected</h3>
                <p style={{ margin: 0 }}>Make sure the backend is running and accessible.</p>
            </div>
        );
    }

    return (
        <>
            {/* All Models or Technical */}
            {(modelSubTab === 'all' || modelSubTab === 'technical') && (
                <>
                    <h2>📊 Technical Models ({models.filter(m => m.category === 'Technical').length})</h2>
                    <p style={{ color: 'var(--muted-foreground)', marginBottom: '15px' }}>Chart patterns, indicators, and price action strategies</p>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '15px', marginBottom: '30px' }}>
                        {models.filter(m => m.category === 'Technical').map(m => (
                            <ModelCard
                                key={m.id}
                                model={m}
                                result={results[m.id]}
                                running={running === m.id}
                                onRun={() => onRun(m.id)}
                                onPDF={onPDF}
                                onEnhancedPDF={onEnhancedPDF}
                                onRunWithParams={(params) => onRunWithParams(m.id, params)}
                            />
                        ))}
                    </div>
                </>
            )}

            {/* All Models or Fundamental */}
            {(modelSubTab === 'all' || modelSubTab === 'fundamental') && (
                <>
                    <h2 style={{ marginTop: modelSubTab === 'all' ? '30px' : '0' }}>💰 Fundamental Models ({models.filter(m => m.category === 'Fundamental').length})</h2>
                    <p style={{ color: 'var(--muted-foreground)', marginBottom: '15px' }}>Value investing, quality metrics, and financial analysis</p>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '15px', marginBottom: '30px' }}>
                        {models.filter(m => m.category === 'Fundamental').map(m => (
                            <ModelCard
                                key={m.id}
                                model={m}
                                result={results[m.id]}
                                running={running === m.id}
                                onRun={() => onRun(m.id)}
                                onPDF={onPDF}
                                onEnhancedPDF={onEnhancedPDF}
                                onRunWithParams={(params) => onRunWithParams(m.id, params)}
                            />
                        ))}
                    </div>
                </>
            )}

            {/* All Models or Quantitative */}
            {(modelSubTab === 'all' || modelSubTab === 'quantitative') && (
                <>
                    <h2 style={{ marginTop: modelSubTab === 'all' ? '30px' : '0' }}>🔢 Quantitative Models ({models.filter(m => m.category === 'Quantitative').length})</h2>
                    <p style={{ color: 'var(--muted-foreground)', marginBottom: '15px' }}>Statistical arbitrage and quantitative strategies</p>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '15px' }}>
                        {models.filter(m => m.category === 'Quantitative').map(m => (
                            <ModelCard
                                key={m.id}
                                model={m}
                                result={results[m.id]}
                                running={running === m.id}
                                onRun={() => onRun(m.id)}
                                onPDF={onPDF}
                                onEnhancedPDF={onEnhancedPDF}
                                onRunWithParams={(params) => onRunWithParams(m.id, params)}
                            />
                        ))}
                    </div>
                </>
            )}
        </>
    );
}
