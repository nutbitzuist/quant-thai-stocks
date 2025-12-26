'use client';

import { useState, useCallback } from 'react';
import { Model, ModelResult, Log, API_URL } from '@/types/dashboard';

interface UseModelsReturn {
    models: Model[];
    results: Record<string, ModelResult>;
    running: string | null;
    loading: boolean;
    error: string | null;
    loadModels: () => Promise<void>;
    runModel: (id: string, universe: string, topN: number) => Promise<void>;
    runModelWithParams: (id: string, universe: string, topN: number, params: Record<string, any>) => Promise<void>;
    setResults: React.Dispatch<React.SetStateAction<Record<string, ModelResult>>>;
}

export function useModels(onLog?: (type: 'info' | 'error' | 'success', message: string) => void): UseModelsReturn {
    const [models, setModels] = useState<Model[]>([]);
    const [results, setResults] = useState<Record<string, ModelResult>>({});
    const [running, setRunning] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const log = useCallback((type: 'info' | 'error' | 'success', message: string) => {
        if (onLog) onLog(type, message);
    }, [onLog]);

    const loadModels = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_URL}/api/models/`);
            if (response.ok) {
                const data = await response.json();
                setModels(data);
                log('success', `Loaded ${data.length} models`);
            } else {
                const errorData = await response.json();
                setError(errorData.detail || 'Failed to load models');
                log('error', errorData.detail || 'Failed to load models');
            }
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Connection error';
            setError(message);
            log('error', message);
        }
        setLoading(false);
    }, [log]);

    const runModel = useCallback(async (id: string, universe: string, topN: number) => {
        setRunning(id);
        log('info', `Running ${id}...`);

        try {
            const response = await fetch(`${API_URL}/api/models/run`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model_id: id, universe, top_n: topN })
            });

            if (response.ok) {
                const data = await response.json();
                setResults(prev => ({ ...prev, [id]: data }));
                log('success', `${data.model_name}: ${data.buy_signals.length} buy, ${data.sell_signals.length} sell`);
            } else {
                const errorData = await response.json();
                log('error', errorData.detail);
            }
        } catch (err) {
            log('error', `${err}`);
        }

        setRunning(null);
    }, [log]);

    const runModelWithParams = useCallback(async (
        id: string,
        universe: string,
        topN: number,
        params: Record<string, any>
    ) => {
        setRunning(id);
        log('info', `Running ${id} with custom parameters...`);

        try {
            const response = await fetch(`${API_URL}/api/models/run`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model_id: id, universe, top_n: topN, parameters: params })
            });

            if (response.ok) {
                const data = await response.json();
                setResults(prev => ({ ...prev, [id]: data }));
                log('success', `${data.model_name}: ${data.buy_signals.length} buy, ${data.sell_signals.length} sell (custom params)`);
            } else {
                const errorData = await response.json();
                log('error', errorData.detail);
            }
        } catch (err) {
            log('error', `${err}`);
        }

        setRunning(null);
    }, [log]);

    return {
        models,
        results,
        running,
        loading,
        error,
        loadModels,
        runModel,
        runModelWithParams,
        setResults,
    };
}

export default useModels;
