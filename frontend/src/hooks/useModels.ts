'use client';

import { useState, useCallback } from 'react';
import { Model, ModelResult, API_URL } from '@/types/dashboard';
import { fetchAPI } from '@/lib/api';
import { toast } from 'sonner';

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
            const data = await fetchAPI<Model[]>(`${API_URL}/api/models/`);
            setModels(data);
            log('success', `Loaded ${data.length} models`);
        } catch (err: any) {
            setError(err.message);
            log('error', err.message);
        }
        setLoading(false);
    }, [log]);

    const runModel = useCallback(async (id: string, universe: string, topN: number) => {
        setRunning(id);
        log('info', `Running ${id}...`);
        const toastId = toast.loading(`Running model ${id}...`);

        try {
            const data = await fetchAPI<ModelResult>(`${API_URL}/api/models/run`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model_id: id, universe, top_n: topN })
            });

            setResults(prev => ({ ...prev, [id]: data }));
            log('success', `${data.model_name}: ${data.buy_signals.length} buy, ${data.sell_signals.length} sell`);
            toast.success(`Model ${data.model_name} completed`, { id: toastId });
        } catch (err: any) {
            log('error', `${err.message}`);
            toast.error(err.message, { id: toastId });
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
        const toastId = toast.loading(`Running model ${id}...`);

        try {
            const data = await fetchAPI<ModelResult>(`${API_URL}/api/models/run`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model_id: id, universe, top_n: topN, parameters: params })
            });

            setResults(prev => ({ ...prev, [id]: data }));
            log('success', `${data.model_name}: ${data.buy_signals.length} buy, ${data.sell_signals.length} sell (custom params)`);
            toast.success(`Model ${data.model_name} completed`, { id: toastId });
        } catch (err: any) {
            log('error', `${err.message}`);
            toast.error(err.message, { id: toastId });
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
