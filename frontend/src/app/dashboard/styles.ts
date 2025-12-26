// Dashboard Shared Styles
// Neo-Brutalist Style Object - HQ0 inspired

import React from 'react';

export const styles = {
    card: {
        background: 'var(--card)',
        color: 'var(--card-foreground)',
        borderRadius: '0',
        padding: '1.25rem',
        marginBottom: '1rem',
        boxShadow: '4px 4px 0 var(--border)',
        border: '3px solid var(--border)',
        transition: 'transform 0.1s ease, box-shadow 0.1s ease'
    } as React.CSSProperties,

    btn: (variant: string) => ({
        padding: '0.625rem 1.25rem',
        background: variant === 'primary' ? 'var(--primary)' : variant === 'success' ? '#22c55e' : variant === 'danger' ? 'var(--destructive)' : 'var(--card)',
        color: variant === 'primary' || variant === 'success' || variant === 'danger' ? '#ffffff' : 'var(--foreground)',
        border: '3px solid var(--border)',
        borderRadius: '0',
        cursor: 'pointer',
        marginRight: '0.5rem',
        fontSize: '0.875rem',
        fontWeight: '700',
        transition: 'transform 0.1s ease, box-shadow 0.1s ease',
        boxShadow: '3px 3px 0 var(--border)',
        textTransform: 'uppercase' as const,
        letterSpacing: '0.5px'
    } as React.CSSProperties),

    select: {
        padding: '0.625rem 0.875rem',
        borderRadius: '0',
        border: '3px solid var(--border)',
        marginRight: '0.625rem',
        fontSize: '0.875rem',
        fontWeight: '600',
        background: 'var(--card)',
        color: 'var(--foreground)',
        boxShadow: '3px 3px 0 var(--border)',
        cursor: 'pointer'
    } as React.CSSProperties,

    tab: (active: boolean) => ({
        padding: '0.625rem 1.25rem',
        background: active ? 'var(--primary)' : 'var(--card)',
        color: active ? '#ffffff' : 'var(--foreground)',
        border: '3px solid var(--border)',
        borderRadius: '0',
        cursor: 'pointer',
        fontWeight: '700',
        fontSize: '0.875rem',
        transition: 'transform 0.1s ease, box-shadow 0.1s ease',
        boxShadow: active ? '4px 4px 0 var(--border)' : '3px 3px 0 var(--border)',
        textTransform: 'uppercase' as const
    } as React.CSSProperties),

    dot: (ok: boolean) => ({
        width: '12px',
        height: '12px',
        borderRadius: '0',
        background: ok ? '#22c55e' : 'var(--destructive)',
        display: 'inline-block',
        marginRight: '0.5rem',
        border: '2px solid var(--border)'
    } as React.CSSProperties),

    input: {
        padding: '0.625rem 0.875rem',
        borderRadius: '0',
        border: '3px solid var(--border)',
        width: '100%',
        marginBottom: '0.625rem',
        fontSize: '0.875rem',
        fontWeight: '500',
        background: 'var(--card)',
        color: 'var(--foreground)',
        transition: 'box-shadow 0.1s ease',
        boxShadow: '2px 2px 0 var(--border)'
    } as React.CSSProperties,

    textarea: {
        padding: '0.625rem 0.875rem',
        borderRadius: '0',
        border: '3px solid var(--border)',
        width: '100%',
        minHeight: '100px',
        marginBottom: '0.625rem',
        fontSize: '0.875rem',
        fontWeight: '500',
        fontFamily: 'var(--font-mono)',
        background: 'var(--card)',
        color: 'var(--foreground)',
        transition: 'box-shadow 0.1s ease',
        boxShadow: '2px 2px 0 var(--border)'
    } as React.CSSProperties,
};

// Short alias for styles
export const S = styles;

// Helper function to remove markdown formatting
export const cleanMarkdown = (text: string): string => {
    if (!text) return text;
    return text.replace(/\*\*/g, '').replace(/\*/g, '').trim();
};

// Helper for market icons
export const getMarketIcon = (market: string) => {
    if (market === 'US') return '🇺🇸';
    if (market === 'Thailand') return '🇹🇭';
    return '🌐';
};

// Format number with commas
export const formatNumber = (num: number, decimals = 2): string => {
    if (num === undefined || num === null || isNaN(num)) return '-';
    return num.toLocaleString(undefined, {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
};

// Format currency
export const formatCurrency = (num: number, currency = 'USD'): string => {
    if (num === undefined || num === null || isNaN(num)) return '-';
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency,
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(num);
};

// Format percentage
export const formatPercent = (num: number, decimals = 2): string => {
    if (num === undefined || num === null || isNaN(num)) return '-';
    return `${num >= 0 ? '+' : ''}${num.toFixed(decimals)}%`;
};
