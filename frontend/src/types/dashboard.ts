// Dashboard TypeScript Types
// Extracted from dashboard/page.tsx for better organization

export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Signal from model run
export interface Signal {
    ticker: string;
    signal_type: string;
    score: number;
    price_at_signal: number;
}

// Model definition
export interface Model {
    id: string;
    name: string;
    description: string;
    category: string;
    default_parameters?: Record<string, any>;
}

// Result from running a model
export interface ModelResult {
    run_id: string;
    model_name: string;
    category: string;
    buy_signals: Signal[];
    sell_signals: Signal[];
    total_stocks_analyzed: number;
    stocks_with_data: number;
}

// Log entry for status display
export interface Log {
    time: string;
    type: 'info' | 'error' | 'success';
    message: string;
}

// Backtest result - supports both simple and VectorBT formats
export interface BacktestResult {
    // Common fields
    model_name?: string;
    strategy_name?: string;
    universe?: string;
    period?: string;
    start_date?: string;
    end_date?: string;

    // Simple backtester format (nested)
    performance?: {
        initial_capital: number;
        final_value: number;
        total_return_pct: number;
        annualized_return_pct: number;
        max_drawdown_pct: number;
        sharpe_ratio: number;
    };
    trades?: {
        total: number;
        winning: number;
        losing: number;
        win_rate_pct: number;
        avg_win_pct: number;
        avg_loss_pct: number;
        profit_factor: number;
    };

    // VectorBT format (flat)
    initial_capital?: number;
    final_value?: number;
    total_return?: number;
    annual_return?: number;
    benchmark_return?: number;
    alpha?: number;
    volatility?: number;
    sharpe_ratio?: number;
    sortino_ratio?: number;
    max_drawdown?: number;
    max_drawdown_duration?: number;
    calmar_ratio?: number;
    total_trades?: number;
    winning_trades?: number;
    losing_trades?: number;
    win_rate?: number;
    avg_win?: number;
    avg_loss?: number;
    profit_factor?: number;
    avg_trade_duration?: number;
    best_day?: number;
    worst_day?: number;
    avg_daily_return?: number;

    // Time series data (VectorBT)
    equity_curve?: Array<{ date: string; value?: number; equity?: number }>;
    drawdown_curve?: Array<{ date: string; drawdown: number }>;
    monthly_returns?: Array<{ month: string; return: number }>;

    // Trades
    recent_trades?: Array<{
        entry_date: string;
        exit_date: string;
        ticker: string;
        entry_price: number;
        exit_price: number;
        return_pct: number;
        pnl: number;
    }>;
}

// Stock analysis types
export interface AnalysisCheckpoint {
    label: string;
    status: 'pass' | 'fail' | 'neutral';
    value: string;
}

export interface AnalysisMetrics {
    market_cap?: number;
    pe_ratio?: number;
    pb_ratio?: number;
    roe?: number;
    profit_margin?: number;
    revenue_growth?: number;
    earnings_growth?: number;
    total_debt?: number;
    debt_to_equity?: number;
    current_ratio?: number;
    free_cash_flow?: number;
    operating_cash_flow?: number;
    forward_pe?: number;
    peg_ratio?: number;
    target_mean_price?: number;
    recommendation_key?: string;
    num_analysts?: number;
}

export interface AnalysisTechnicals {
    rsi?: number;
    macd?: number;
    macd_signal?: number;
    sma_200?: number;
    return_1y?: number;
    close?: number;
}

export interface AnalysisData {
    ticker: string;
    name: string;
    price: number;
    currency: string;
    score: number;
    recommendation: string;
    summary: string;
    metrics: AnalysisMetrics;
    technicals: AnalysisTechnicals;
    checkpoints: AnalysisCheckpoint[];
}

// Universe types
export interface Universe {
    id: string;
    name: string;
    market: string;
    count: number;
    description?: string;
}

export interface CustomUniverse {
    id: string;
    name: string;
    symbols: string[];
    market?: string;
    count?: number;
}

// Tab types
export type TabType = 'models' | 'results' | 'backtest' | 'analyze' | 'status';
