'use client';

import { useState, useCallback, useRef } from 'react';
import { Log } from '@/types/dashboard';

interface UseLogsReturn {
    logs: Log[];
    log: (type: Log['type'], message: string) => void;
    clearLogs: () => void;
}

export function useLogs(maxLogs = 100): UseLogsReturn {
    const [logs, setLogs] = useState<Log[]>([]);
    const logIdRef = useRef(0);

    const log = useCallback((type: Log['type'], message: string) => {
        const now = new Date();
        const time = now.toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });

        setLogs(prev => {
            const newLog: Log = { time, type, message };
            const updated = [newLog, ...prev];
            // Keep only the last maxLogs entries
            return updated.slice(0, maxLogs);
        });
    }, [maxLogs]);

    const clearLogs = useCallback(() => {
        setLogs([]);
    }, []);

    return { logs, log, clearLogs };
}

export default useLogs;
