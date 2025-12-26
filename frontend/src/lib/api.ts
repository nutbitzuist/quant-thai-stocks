import { toast } from 'sonner';

/**
 * Unified API Client for handling requests with automatic error notifications
 */

// Types for standard API responses
interface APIResponse<T = any> {
    data?: T;
    message?: string;
    [key: string]: any;
}

interface RequestOptions extends RequestInit {
    skipErrorToast?: boolean;
}

/**
 * Fetch wrapper that handles errors and toasts automatically
 */
export async function fetchAPI<T = any>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const { skipErrorToast, ...fetchOptions } = options;

    // Inject Auth Headers
    const headers = new Headers(fetchOptions.headers);

    // safe access to localStorage for SSR
    if (typeof window !== 'undefined') {
        const userId = localStorage.getItem('quant_user_id');
        const apiKey = localStorage.getItem('quant_api_key');

        // Use stored credentials or fallbacks for demo/MVP
        headers.set('X-User-ID', userId || 'demo-user');
        if (apiKey) {
            headers.set('X-API-Key', apiKey);
        }
    } else {
        // Server-side fallback
        headers.set('X-User-ID', 'demo-user');
    }

    fetchOptions.headers = headers;

    try {
        const res = await fetch(endpoint, fetchOptions);

        // Try to parse JSON, but handle non-JSON responses gracefully
        let data: any;
        const contentType = res.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            data = await res.json();
        } else {
            data = { message: await res.text() };
        }

        if (!res.ok) {
            // Throw error with message from backend if available
            throw new Error(data.detail || data.message || `Error ${res.status}: ${res.statusText}`);
        }

        return data as T;
    } catch (err: any) {
        console.error(`API Error (${endpoint}):`, err);

        if (!skipErrorToast) {
            toast.error(err.message || "An unexpected error occurred");
        }

        throw err;
    }
}
