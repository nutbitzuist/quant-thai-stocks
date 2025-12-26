'use client';

import { useState, useCallback } from 'react';
import { BacktestResult, API_URL } from '@/types/dashboard';

interface BacktestParams {
    model_id: string;
    universe: string;
    initial_capital: number;
    max_positions?: number;
    position_size?: number;
    stop_loss?: number | null;
    take_profit?: number | null;
    rebalance_freq?: string;
}

interface UseBacktestReturn {
    result: BacktestResult | null;
    running: boolean;
    error: string | null;
    tearsheetData: string | null;
    runBacktest: (params: BacktestParams, useVectorBT?: boolean) => Promise<void>;
    fetchTearsheet: (modelId: string, universe: string) => Promise<void>;
    clearResult: () => void;
}

export function useBacktest(onLog?: (type: 'info' | 'error' | 'success', message: string) => void): UseBacktestReturn {
    const [result, setResult] = useState<BacktestResult | null>(null);
    const [running, setRunning] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [tearsheetData, setTearsheetData] = useState<string | null>(null);

    const log = useCallback((type: 'info' | 'error' | 'success', message: string) => {
        if (onLog) onLog(type, message);
    }, [onLog]);

    const runBacktest = useCallback(async (params: BacktestParams, useVectorBT = true) => {
        setRunning(true);
        setError(null);
        setTearsheetData(null);

        const endpoint = useVectorBT
            ? `${API_URL}/api/backtest/run`
            : `${API_URL}/api/advanced/backtest`;

        log('info', `Running ${useVectorBT ? 'advanced' : 'simple'} backtest for ${params.model_id}...`);

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(params)
            });

            if (response.ok) {
                const data = await response.json();
                setResult(data);

                // Calculate return for logging
                const totalReturn = data.total_return ?? data.performance?.total_return_pct ?? 0;
                const returnStr = totalReturn >= 0 ? `+${totalReturn.toFixed(2)}%` : `${totalReturn.toFixed(2)}%`;
                log('success', `Backtest complete: ${returnStr} return`);
            } else {
                const errorData = await response.json();
                const errorMessage = errorData.detail || 'Backtest failed';
                setError(errorMessage);
                log('error', errorMessage);
            }
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Connection error';
            setError(message);
            log('error', message);
        }

        setRunning(false);
    }, [log]);

    const fetchTearsheet = useCallback(async (modelId: string, universe: string) => {
        log('info', 'Generating QuantStats tearsheet...');

        try {
            const response = await fetch(
                `${API_URL}/api/backtest/tearsheet?model_id=${modelId}&universe=${universe}`
            );

            if (response.ok) {
                const html = await response.text();
                setTearsheetData(html);
                log('success', 'Tearsheet generated successfully');
            } else {
                log('error', 'Failed to generate tearsheet');
            }
        } catch (err) {
            log('error', `Tearsheet error: ${err}`);
        }
    }, [log]);

    const clearResult = useCallback(() => {
        setResult(null);
        setTearsheetData(null);
        setError(null);
    }, []);

    return {
        result,
        running,
        error,
        tearsheetData,
        runBacktest,
        fetchTearsheet,
        clearResult,
    };
}

export default useBacktest;
