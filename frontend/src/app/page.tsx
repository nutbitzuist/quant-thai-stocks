'use client';

import { useState, useEffect } from 'react';

// API URL - can be overridden by environment variable
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Types
interface Signal { ticker: string; signal_type: string; score: number; price_at_signal: number; }
interface Model { id: string; name: string; description: string; category: string; default_parameters?: Record<string, any>; }
interface ModelResult { run_id: string; model_name: string; category: string; buy_signals: Signal[]; sell_signals: Signal[]; total_stocks_analyzed: number; stocks_with_data: number; }
interface Log { time: string; type: 'info' | 'error' | 'success'; message: string; }
interface BacktestResult {
  model_name: string;
  universe: string;
  period: string;
  performance: {
    initial_capital: number;
    final_value: number;
    total_return_pct: number;
    annualized_return_pct: number;
    max_drawdown_pct: number;
    sharpe_ratio: number;
  };
  trades: {
    total: number;
    winning: number;
    losing: number;
    win_rate_pct: number;
    avg_win_pct: number;
    avg_loss_pct: number;
    profit_factor: number;
  };
  equity_curve: Array<{ date: string; equity: number }>;
  recent_trades: Array<{
    entry_date: string;
    exit_date: string;
    ticker: string;
    entry_price: number;
    exit_price: number;
    return_pct: number;
    pnl: number;
  }>;
}

// Helper function to remove markdown formatting
const cleanMarkdown = (text: string): string => {
  if (!text) return text;
  // Remove both single and double asterisks (markdown bold/italic)
  return text.replace(/\*\*/g, '').replace(/\*/g, '').trim();
};

const S = {
  card: { 
    background: 'var(--card)', 
    color: 'var(--card-foreground)',
    borderRadius: 'var(--radius)', 
    padding: '1.25rem', 
    marginBottom: '1rem', 
    boxShadow: 'var(--shadow-sm)',
    border: '1px solid var(--border)'
  } as React.CSSProperties,
  btn: (v: string) => ({ 
    padding: '0.5rem 1rem', 
    background: v === 'primary' ? 'var(--primary)' : v === 'success' ? '#22c55e' : v === 'danger' ? 'var(--destructive)' : 'var(--secondary)', 
    color: v === 'primary' || v === 'success' || v === 'danger' ? 'var(--primary-foreground)' : 'var(--secondary-foreground)', 
    border: 'none', 
    borderRadius: 'var(--radius)', 
    cursor: 'pointer', 
    marginRight: '0.5rem', 
    fontSize: '0.875rem',
    fontWeight: '500',
    transition: 'all 0.2s ease',
    boxShadow: 'var(--shadow-xs)'
  } as React.CSSProperties & { onMouseEnter?: (e: React.MouseEvent<HTMLButtonElement>) => void; onMouseLeave?: (e: React.MouseEvent<HTMLButtonElement>) => void }),
  select: { 
    padding: '0.5rem 0.75rem', 
    borderRadius: 'var(--radius)', 
    border: '1px solid var(--input)', 
    marginRight: '0.625rem', 
    fontSize: '0.875rem',
    background: 'var(--background)',
    color: 'var(--foreground)'
  } as React.CSSProperties,
  tab: (a: boolean) => ({ 
    padding: '0.5rem 1rem', 
    background: a ? 'var(--primary)' : 'transparent', 
    color: a ? 'var(--primary-foreground)' : 'var(--muted-foreground)', 
    border: 'none', 
    borderRadius: 'var(--radius)', 
    cursor: 'pointer', 
    fontWeight: a ? '600' : 'normal' as const, 
    fontSize: '0.875rem',
    transition: 'all 0.2s ease',
    ...(a ? {} : { ':hover': { background: 'var(--muted)' } })
  } as React.CSSProperties),
  dot: (ok: boolean) => ({ 
    width: '10px', 
    height: '10px', 
    borderRadius: '50%', 
    background: ok ? '#22c55e' : 'var(--destructive)', 
    display: 'inline-block', 
    marginRight: '0.5rem',
    boxShadow: 'var(--shadow-xs)'
  } as React.CSSProperties),
  input: { 
    padding: '0.5rem 0.75rem', 
    borderRadius: 'var(--radius)', 
    border: '1px solid var(--input)', 
    width: '100%', 
    marginBottom: '0.625rem', 
    fontSize: '0.875rem',
    background: 'var(--background)',
    color: 'var(--foreground)',
    transition: 'border-color 0.2s ease'
  } as React.CSSProperties,
  textarea: { 
    padding: '0.5rem 0.75rem', 
    borderRadius: 'var(--radius)', 
    border: '1px solid var(--input)', 
    width: '100%', 
    minHeight: '100px', 
    marginBottom: '0.625rem', 
    fontSize: '0.875rem', 
    fontFamily: 'var(--font-mono)',
    background: 'var(--background)',
    color: 'var(--foreground)',
    transition: 'border-color 0.2s ease'
  } as React.CSSProperties,
};

export default function Home() {
  const [tab, setTab] = useState<'models'|'advanced'|'backtest'|'universe'|'model-detail'|'history'|'status'|'settings'>('models');
  const [models, setModels] = useState<Model[]>([]);
  const [results, setResults] = useState<Record<string, ModelResult>>({});
  const [running, setRunning] = useState<string|null>(null);
  const [universe, setUniverse] = useState('sp50');
  const [topN, setTopN] = useState(10); // Number of top signals to show
  const [universes, setUniverses] = useState<any[]>([]);
  const [customUniverses, setCustomUniverses] = useState<any[]>([]);
  const [connected, setConnected] = useState(false);
  const [logs, setLogs] = useState<Log[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [modelDocs, setModelDocs] = useState<Record<string, any>>({});
  const [selDoc, setSelDoc] = useState<string|null>(null);
  const [newUni, setNewUni] = useState({ name: '', desc: '', tickers: '', market: 'US' });
  
  // Backtesting state
  const [backtestModel, setBacktestModel] = useState<string>('');
  const [backtestUniverse, setBacktestUniverse] = useState('sp50');
  const [backtestCapital, setBacktestCapital] = useState(100000);
  const [backtestHoldingPeriod, setBacktestHoldingPeriod] = useState(21);
  const [backtestTopN, setBacktestTopN] = useState(10);
  const [backtestRunning, setBacktestRunning] = useState(false);
  const [backtestResults, setBacktestResults] = useState<BacktestResult | null>(null);
  
  // Advanced features state
  const [signalCombinerUniverse, setSignalCombinerUniverse] = useState('sp50');
  const [signalCombinerMinConf, setSignalCombinerMinConf] = useState(3);
  const [signalCombinerCategory, setSignalCombinerCategory] = useState<string>('');
  const [signalCombinerRunning, setSignalCombinerRunning] = useState(false);
  const [signalCombinerResults, setSignalCombinerResults] = useState<any>(null);
  
  const [sectorRotationUniverse, setSectorRotationUniverse] = useState('sp500');
  const [sectorRotationRunning, setSectorRotationRunning] = useState(false);
  const [sectorRotationResults, setSectorRotationResults] = useState<any>(null);
  
  // Market Regime state
  const [marketRegimeIndex, setMarketRegimeIndex] = useState('SPY');
  const [marketRegimeUniverse, setMarketRegimeUniverse] = useState('sp50');
  const [marketRegimeRunning, setMarketRegimeRunning] = useState(false);
  const [marketRegimeResults, setMarketRegimeResults] = useState<any>(null);
  
  // Scheduled Scans state
  const [scheduledScans, setScheduledScans] = useState<any[]>([]);
  const [newScanModel, setNewScanModel] = useState('');
  const [newScanUniverse, setNewScanUniverse] = useState('sp50');
  const [newScanTime, setNewScanTime] = useState('09:30');
  const [newScanDays, setNewScanDays] = useState<string[]>(['Mon', 'Tue', 'Wed', 'Thu', 'Fri']);
  
  // Universe details state
  const [selectedUniverseId, setSelectedUniverseId] = useState<string | null>(null);
  const [universeDetails, setUniverseDetails] = useState<any>(null);
  const [universeStocks, setUniverseStocks] = useState<any[]>([]);
  const [selectedStock, setSelectedStock] = useState<string | null>(null);
  const [stockDetails, setStockDetails] = useState<any>(null);
  
  // Custom universe edit state
  const [editingUniverse, setEditingUniverse] = useState<any>(null);
  const [parsePreview, setParsePreview] = useState<any>(null);

  const log = (t: Log['type'], m: string) => setLogs(p => [...p.slice(-99), { time: new Date().toLocaleTimeString(), type: t, message: m }]);

  const checkConn = async () => {
    try { const r = await fetch(`${API_URL}/api/status/test-connection`); if (r.ok) { setConnected(true); log('success', 'Connected'); return true; } } catch(e) { log('error', `Connection failed: ${e}`); }
    setConnected(false); return false;
  };

  const loadAll = async () => {
    try { const r = await fetch(`${API_URL}/api/models/`); if (r.ok) { const d = await r.json(); setModels(d.models); log('success', `Loaded ${d.models.length} models`); } } catch(e) { log('error', `${e}`); }
    try { const r = await fetch(`${API_URL}/api/universe/`); if (r.ok) { const d = await r.json(); setUniverses(d.universes); } } catch(e) {}
    try { const r = await fetch(`${API_URL}/api/custom-universe/`); if (r.ok) { const d = await r.json(); setCustomUniverses(d.universes); } } catch(e) {}
    try { const r = await fetch(`${API_URL}/api/models/docs`); if (r.ok) { const d = await r.json(); setModelDocs(d); } } catch(e) {}
    try { 
      const r = await fetch(`${API_URL}/api/models/history`); 
      if (r.ok) { 
        const d = await r.json(); 
        setHistory(d.runs || []); 
        if (d.runs && d.runs.length > 0) {
          log('info', `Loaded ${d.runs.length} history records`);
        }
      } else {
        const errorText = await r.text();
        log('error', `Failed to load history: ${r.status} ${errorText}`);
      }
    } catch(e: any) { 
      log('error', `Failed to load history: ${e.message || e}`); 
    }
  };

  const runModel = async (id: string) => {
    setRunning(id); log('info', `Running ${id}...`);
    try {
      const r = await fetch(`${API_URL}/api/models/run`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ model_id: id, universe, top_n: topN }) });
      if (r.ok) { const d = await r.json(); setResults(p => ({ ...p, [id]: d })); log('success', `${d.model_name}: ${d.buy_signals.length} buy, ${d.sell_signals.length} sell (showing top ${topN})`); loadAll(); }
      else { const e = await r.json(); log('error', e.detail); }
    } catch(e) { log('error', `${e}`); }
    setRunning(null);
  };

  const runModelWithParams = async (id: string, params: Record<string, any>) => {
    setRunning(id); log('info', `Running ${id} with custom parameters...`);
    try {
      const r = await fetch(`${API_URL}/api/models/run`, { 
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' }, 
        body: JSON.stringify({ model_id: id, universe, top_n: topN, parameters: params }) 
      });
      if (r.ok) { 
        const d = await r.json(); 
        setResults(p => ({ ...p, [id]: d })); 
        log('success', `${d.model_name}: ${d.buy_signals.length} buy, ${d.sell_signals.length} sell (custom params)`); 
        loadAll(); 
      }
      else { const e = await r.json(); log('error', e.detail); }
    } catch(e) { log('error', `${e}`); }
    setRunning(null);
  };

  const runBacktest = async () => {
    if (!backtestModel) { log('error', 'Please select a model'); return; }
    setBacktestRunning(true);
    log('info', `Running backtest for ${backtestModel}...`);
    try {
      const r = await fetch(`${API_URL}/api/advanced/backtest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model_id: backtestModel,
          universe: backtestUniverse,
          initial_capital: backtestCapital,
          holding_period: backtestHoldingPeriod,
          top_n: backtestTopN
        })
      });
      if (r.ok) {
        const d = await r.json();
        setBacktestResults(d);
        log('success', `Backtest complete: ${d.performance.total_return_pct.toFixed(2)}% return, ${d.trades.win_rate_pct.toFixed(1)}% win rate`);
      } else {
        const e = await r.json();
        log('error', `Backtest failed: ${e.detail || r.statusText}`);
      }
    } catch(e) {
      log('error', `Backtest error: ${e}`);
    }
    setBacktestRunning(false);
  };

  const downloadBacktestPDF = async (result: BacktestResult) => {
    try {
      log('info', 'Generating PDF...');
      const r = await fetch(`${API_URL}/api/advanced/backtest/export-pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(result)
      });
      if (r.ok) {
        const contentType = r.headers.get('content-type');
        if (contentType && contentType.includes('application/pdf')) {
          const contentDisposition = r.headers.get('content-disposition');
          let filename = 'backtest.pdf';
          if (contentDisposition) {
            const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
            if (match && match[1]) {
              filename = match[1].replace(/['"]/g, '');
            }
          }
          const b = await r.blob();
          const u = URL.createObjectURL(b);
          const a = document.createElement('a');
          a.href = u;
          a.download = filename;
          a.click();
          URL.revokeObjectURL(u);
          log('success', `PDF downloaded: ${filename}`);
        } else {
          const errorText = await r.text();
          log('error', `Expected PDF but got: ${errorText.substring(0, 100)}`);
        }
      } else {
        const errorData = await r.json().catch(() => ({ detail: r.statusText }));
        log('error', `PDF download failed: ${errorData.detail || r.statusText}`);
      }
    } catch(e) {
      log('error', `PDF download error: ${e}`);
    }
  };

  const runSignalCombiner = async () => {
    setSignalCombinerRunning(true);
    log('info', 'Running signal combiner...');
    try {
      const body: any = {
        universe: signalCombinerUniverse,
        min_confirmation: signalCombinerMinConf
      };
      if (signalCombinerCategory) {
        body.category = signalCombinerCategory;
      }
      
      const r = await fetch(`${API_URL}/api/advanced/signal-combiner`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      if (r.ok) {
        const d = await r.json();
        setSignalCombinerResults(d);
        log('success', `Signal combiner: ${d.strong_buy_signals?.length || 0} strong buys, ${d.strong_sell_signals?.length || 0} strong sells`);
      } else {
        const e = await r.json();
        log('error', `Signal combiner failed: ${e.detail || r.statusText}`);
      }
    } catch(e) {
      log('error', `Signal combiner error: ${e}`);
    }
    setSignalCombinerRunning(false);
  };

  const runSectorRotation = async () => {
    setSectorRotationRunning(true);
    log('info', 'Analyzing sector rotation...');
    try {
      const r = await fetch(`${API_URL}/api/advanced/sector-rotation?universe=${sectorRotationUniverse}`);
      if (r.ok) {
        const d = await r.json();
        setSectorRotationResults(d);
        log('success', `Sector rotation: ${d.rotation_recommendation?.summary || 'Analysis complete'}`);
      } else {
        const e = await r.json();
        log('error', `Sector rotation failed: ${e.detail || r.statusText}`);
      }
    } catch(e) {
      log('error', `Sector rotation error: ${e}`);
    }
    setSectorRotationRunning(false);
  };

  const runMarketRegime = async () => {
    setMarketRegimeRunning(true);
    log('info', 'Detecting market regime...');
    try {
      const r = await fetch(`${API_URL}/api/advanced/market-regime?index=${marketRegimeIndex}&universe=${marketRegimeUniverse}`);
      if (r.ok) {
        const d = await r.json();
        setMarketRegimeResults(d);
        log('success', `Market Regime: ${d.regime} - ${d.recommendation || 'Analysis complete'}`);
      } else {
        const e = await r.json();
        log('error', `Market regime failed: ${e.detail || r.statusText}`);
      }
    } catch(e) {
      log('error', `Market regime error: ${e}`);
    }
    setMarketRegimeRunning(false);
  };

  // Scheduled Scans functions
  const loadScheduledScans = async () => {
    try {
      const r = await fetch(`${API_URL}/api/scheduled-scans/`);
      if (r.ok) {
        const d = await r.json();
        setScheduledScans(d.scans || []);
      }
    } catch(e) { /* Scheduled scans endpoint may not exist yet */ }
  };

  const createScheduledScan = async () => {
    if (!newScanModel) { log('error', 'Please select a model'); return; }
    try {
      const r = await fetch(`${API_URL}/api/scheduled-scans/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model_id: newScanModel,
          universe: newScanUniverse,
          schedule_time: newScanTime,
          days: newScanDays,
          enabled: true
        })
      });
      if (r.ok) {
        log('success', 'Scheduled scan created');
        loadScheduledScans();
        setNewScanModel('');
      } else {
        const e = await r.json();
        log('error', `Failed to create scan: ${e.detail || r.statusText}`);
      }
    } catch(e) {
      log('error', `Create scan error: ${e}`);
    }
  };

  const deleteScheduledScan = async (scanId: string) => {
    try {
      const r = await fetch(`${API_URL}/api/scheduled-scans/${scanId}`, { method: 'DELETE' });
      if (r.ok) {
        log('success', 'Scheduled scan deleted');
        loadScheduledScans();
      }
    } catch(e) {
      log('error', `Delete scan error: ${e}`);
    }
  };

  const toggleScheduledScan = async (scanId: string, enabled: boolean) => {
    try {
      const r = await fetch(`${API_URL}/api/scheduled-scans/${scanId}/toggle`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled })
      });
      if (r.ok) {
        log('success', `Scan ${enabled ? 'enabled' : 'disabled'}`);
        loadScheduledScans();
      }
    } catch(e) {
      log('error', `Toggle scan error: ${e}`);
    }
  };

  const downloadSignalCombinerPDF = async (result: any) => {
    try {
      log('info', 'Generating Signal Combiner PDF...');
      const r = await fetch(`${API_URL}/api/advanced/signal-combiner/export-pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(result)
      });
      if (r.ok) {
        const contentType = r.headers.get('content-type');
        if (contentType && contentType.includes('application/pdf')) {
          const contentDisposition = r.headers.get('content-disposition');
          let filename = 'signal_combiner.pdf';
          if (contentDisposition) {
            const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
            if (match && match[1]) {
              filename = match[1].replace(/['"]/g, '');
            }
          }
          const b = await r.blob();
          const u = URL.createObjectURL(b);
          const a = document.createElement('a');
          a.href = u;
          a.download = filename;
          a.click();
          URL.revokeObjectURL(u);
          log('success', `PDF downloaded: ${filename}`);
        } else {
          const errorText = await r.text();
          log('error', `Expected PDF but got: ${errorText.substring(0, 100)}`);
        }
      } else {
        const errorData = await r.json().catch(() => ({ detail: r.statusText }));
        log('error', `PDF download failed: ${errorData.detail || r.statusText}`);
      }
    } catch(e) {
      log('error', `PDF download error: ${e}`);
    }
  };

  const downloadSectorRotationPDF = async (result: any) => {
    try {
      log('info', 'Generating Sector Rotation PDF...');
      const r = await fetch(`${API_URL}/api/advanced/sector-rotation/export-pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(result)
      });
      if (r.ok) {
        const contentType = r.headers.get('content-type');
        if (contentType && contentType.includes('application/pdf')) {
          const contentDisposition = r.headers.get('content-disposition');
          let filename = 'sector_rotation.pdf';
          if (contentDisposition) {
            const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
            if (match && match[1]) {
              filename = match[1].replace(/['"]/g, '');
            }
          }
          const b = await r.blob();
          const u = URL.createObjectURL(b);
          const a = document.createElement('a');
          a.href = u;
          a.download = filename;
          a.click();
          URL.revokeObjectURL(u);
          log('success', `PDF downloaded: ${filename}`);
        } else {
          const errorText = await r.text();
          log('error', `Expected PDF but got: ${errorText.substring(0, 100)}`);
        }
      } else {
        const errorData = await r.json().catch(() => ({ detail: r.statusText }));
        log('error', `PDF download failed: ${errorData.detail || r.statusText}`);
      }
    } catch(e) {
      log('error', `PDF download error: ${e}`);
    }
  };


  const downloadBacktestCSV = async (result: BacktestResult) => {
    try {
      log('info', 'Generating CSV...');
      const r = await fetch(`${API_URL}/api/advanced/backtest/export-csv`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(result)
      });
      if (r.ok) {
        const contentType = r.headers.get('content-type');
        if (contentType && contentType.includes('text/csv')) {
          const contentDisposition = r.headers.get('content-disposition');
          let filename = 'backtest.csv';
          if (contentDisposition) {
            const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
            if (match && match[1]) {
              filename = match[1].replace(/['"]/g, '');
            }
          }
          const b = await r.blob();
          const u = URL.createObjectURL(b);
          const a = document.createElement('a');
          a.href = u;
          a.download = filename;
          a.click();
          URL.revokeObjectURL(u);
          log('success', `CSV downloaded: ${filename}`);
        } else {
          const errorText = await r.text();
          log('error', `Expected CSV but got: ${errorText.substring(0, 100)}`);
        }
      } else {
        const errorData = await r.json().catch(() => ({ detail: r.statusText }));
        log('error', `CSV download failed: ${errorData.detail || r.statusText}`);
      }
    } catch(e) {
      log('error', `CSV download error: ${e}`);
    }
  };

  const downloadPDF = async (id: string) => {
    try {
      log('info', `Downloading PDF for run: ${id}`);
      const r = await fetch(`${API_URL}/api/models/history/${id}/pdf`);
      if (r.ok) {
        const contentType = r.headers.get('content-type');
        if (contentType && contentType.includes('application/pdf')) {
          // Extract filename from Content-Disposition header
          const contentDisposition = r.headers.get('content-disposition');
          let filename = `${id}.pdf`; // fallback
          if (contentDisposition) {
            // Try multiple patterns to extract filename
            // Pattern 1: filename="value" or filename='value'
            let match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
            if (match && match[1]) {
              filename = match[1].replace(/['"]/g, '');
            } else {
              // Pattern 2: filename*=UTF-8''value
              match = contentDisposition.match(/filename\*=UTF-8''([^;\n]*)/);
              if (match && match[1]) {
                filename = decodeURIComponent(match[1]);
              } else {
                // Pattern 3: filename=value (no quotes)
                match = contentDisposition.match(/filename=([^;\n]+)/);
                if (match && match[1]) {
                  filename = match[1].trim();
                }
              }
            }
            log('info', `Extracted filename from header: ${filename}`);
          } else {
            log('info', 'No Content-Disposition header found, using fallback filename');
          }
          
          const b = await r.blob();
          const u = URL.createObjectURL(b);
          const a = document.createElement('a');
          a.href = u;
          a.download = filename;
          a.click();
          URL.revokeObjectURL(u);
          log('success', `PDF downloaded: ${filename}`);
        } else {
          const errorText = await r.text();
          log('error', `Expected PDF but got: ${errorText.substring(0, 100)}`);
        }
      } else {
        const errorData = await r.json().catch(() => ({ detail: r.statusText }));
        log('error', `PDF download failed: ${errorData.detail || r.statusText}`);
      }
    } catch(e) {
      log('error', `PDF download error: ${e}`);
    }
  };

  const createUniverse = async () => {
    try {
      const r = await fetch(`${API_URL}/api/custom-universe/import`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: newUni.name, description: newUni.desc, ticker_text: newUni.tickers, market: newUni.market }) });
      if (r.ok) { log('success', 'Universe created'); setNewUni({ name: '', desc: '', tickers: '', market: 'US' }); setParsePreview(null); loadAll(); }
    } catch(e) { log('error', `${e}`); }
  };

  const parseTickerText = async () => {
    if (!newUni.tickers.trim()) { setParsePreview(null); return; }
    try {
      const formData = new FormData();
      formData.append('ticker_text', newUni.tickers);
      const r = await fetch(`${API_URL}/api/custom-universe/parse`, {
        method: 'POST',
        body: formData
      });
      if (r.ok) {
        const d = await r.json();
        setParsePreview(d);
        log('info', `Preview: ${d.tickers?.length || 0} tickers found`);
      }
    } catch(e) { log('error', `Parse error: ${e}`); }
  };

  const updateCustomUniverse = async (universeId: string, name: string, desc: string, tickers: string, market: string) => {
    try {
      const r = await fetch(`${API_URL}/api/custom-universe/${universeId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description: desc, tickers: tickers.split(',').map((t: string) => t.trim()).filter((t: string) => t), market })
      });
      if (r.ok) {
        log('success', 'Universe updated');
        setEditingUniverse(null);
        loadAll();
      } else {
        const e = await r.json();
        log('error', `Update failed: ${e.detail || r.statusText}`);
      }
    } catch(e) { log('error', `Update error: ${e}`); }
  };

  const deleteCustomUniverse = async (universeId: string) => {
    if (!confirm('Are you sure you want to delete this universe?')) return;
    try {
      const r = await fetch(`${API_URL}/api/custom-universe/${universeId}`, { method: 'DELETE' });
      if (r.ok) {
        log('success', 'Universe deleted');
        loadAll();
      } else {
        const e = await r.json();
        log('error', `Delete failed: ${e.detail || r.statusText}`);
      }
    } catch(e) { log('error', `Delete error: ${e}`); }
  };


  const loadUniverseDetails = async (universeId: string) => {
    setSelectedUniverseId(universeId);
    setUniverseDetails(null);
    setUniverseStocks([]);
    try {
      const r = await fetch(`${API_URL}/api/universe/${universeId}`);
      if (r.ok) {
        const d = await r.json();
        setUniverseDetails(d);
      } else {
        const errorText = await r.text();
        log('error', `Failed to load universe details: ${r.status} ${errorText}`);
      }
    } catch(e: any) { 
      log('error', `Failed to load universe details: ${e.message || e}`); 
    }
    
    try {
      const r2 = await fetch(`${API_URL}/api/universe/${universeId}/stocks`);
      if (r2.ok) {
        const d2 = await r2.json();
        setUniverseStocks(d2.stocks || []);
      } else {
        const errorText = await r2.text();
        log('error', `Failed to load universe stocks: ${r2.status} ${errorText}`);
      }
    } catch(e: any) { 
      log('error', `Failed to load universe stocks: ${e.message || e}`); 
    }
  };

  const loadStockDetails = async (ticker: string) => {
    setSelectedStock(ticker);
    try {
      const r = await fetch(`${API_URL}/api/universe/stock/${ticker}`);
      if (r.ok) {
        const d = await r.json();
        setStockDetails(d);
      }
    } catch(e) { log('error', `Failed to load stock details: ${e}`); }
  };

  const clearHistory = async () => {
    if (!confirm('Are you sure you want to clear all run history?')) return;
    try {
      const r = await fetch(`${API_URL}/api/models/history`, { method: 'DELETE' });
      if (r.ok) {
        log('success', 'History cleared');
        loadAll();
      } else {
        const e = await r.json();
        log('error', `Clear failed: ${e.detail || r.statusText}`);
      }
    } catch(e) { log('error', `Clear error: ${e}`); }
  };

  const clearCache = async () => {
    try {
      const r = await fetch(`${API_URL}/api/status/clear-cache`, { method: 'POST' });
      if (r.ok) {
        log('success', 'Cache cleared');
      } else {
        const e = await r.json();
        log('error', `Clear cache failed: ${e.detail || r.statusText}`);
      }
    } catch(e) { log('error', `Clear cache error: ${e}`); }
  };

  const testDataFetch = async () => {
    try {
      log('info', 'Testing data fetch...');
      const r = await fetch(`${API_URL}/api/status/test-data`);
      if (r.ok) {
        const d = await r.json();
        log('success', `Data fetch test: ${d.conclusion}`);
        if (d.price_data?.status === 'success') {
          log('info', `Price data: ${d.price_data.rows} rows, latest: $${d.price_data.latest_close}`);
        }
        if (d.fundamental_data?.status === 'success') {
          log('info', `Fundamental data: ${d.fundamental_data.name} - P/E: ${d.fundamental_data.pe_ratio}`);
        }
      }
    } catch(e) { log('error', `Test failed: ${e}`); }
  };

  const loadStatusLogs = async () => {
    try {
      const r = await fetch(`${API_URL}/api/status/logs`);
      if (r.ok) {
        const d = await r.json();
        if (d.fetch_errors && d.fetch_errors.length > 0) {
          log('info', `Found ${d.fetch_errors.length} fetch errors in system logs`);
        }
      }
    } catch(e) { log('error', `Failed to load logs: ${e}`); }
  };

  useEffect(() => { 
    checkConn().then(ok => {
      if (ok) {
        loadAll();
      }
    }); 
  }, []);

  // Reload history when history tab is opened
  useEffect(() => {
    if (tab === 'history') {
      loadAll();
    }
  }, [tab]);

  return (
    <div style={{ minHeight: '100vh', background: 'var(--background)', color: 'var(--foreground)' }}>
      {/* Header */}
      <div style={{ background: 'var(--card)', borderBottom: '1px solid var(--border)', padding: '1rem 1.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: 'var(--shadow-sm)' }}>
        <div><h1 style={{ margin: 0, fontSize: '1.25rem', fontWeight: '600', color: 'var(--foreground)' }}>📈 Quant Stock Analysis v2.0.2</h1></div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <span style={S.dot(connected)} />
          <select style={{ ...S.select, background: 'var(--background)' }} value={universe} onChange={e => setUniverse(e.target.value)}>
            <optgroup label="Built-in">{universes.map(u => <option key={u.id} value={u.id}>{u.name} ({u.count})</option>)}</optgroup>
            {customUniverses.length > 0 && <optgroup label="Custom">{customUniverses.map(u => <option key={u.id} value={u.id}>{u.name} ({u.count})</option>)}</optgroup>}
          </select>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', background: 'var(--card)', padding: '0.75rem 1.25rem', borderBottom: '1px solid var(--border)', flexWrap: 'wrap' }}>
        {(['models', 'advanced', 'backtest', 'universe', 'model-detail', 'history', 'status', 'settings'] as const).map(t => (
          <button key={t} style={S.tab(tab === t)} onClick={() => setTab(t)}>
            {t === 'models' ? '📚 Models' : t === 'advanced' ? '⚡ Advanced' : t === 'backtest' ? '📊 Backtest' : t === 'universe' ? '🌐 Universe' : t === 'model-detail' ? '📖 Model Details' : t === 'history' ? '📜 History' : t === 'status' ? '🔧 Status' : '⚙️ Settings'}
          </button>
        ))}
      </div>

      <div style={{ padding: '1.25rem', maxWidth: '1400px', margin: '0 auto' }}>
        {/* Connection Warning */}
        {!connected && <div style={{ ...S.card, background: 'var(--accent)', borderLeft: '4px solid var(--primary)', color: 'var(--accent-foreground)' }}><h3 style={{ margin: '0 0 0.5rem 0' }}>⚠️ Backend Not Connected</h3><p style={{ margin: 0 }}>Make sure the backend is running and accessible.</p></div>}

        {/* HISTORY */}
        {tab === 'history' && (
          <div style={S.card}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
              <h2 style={{ margin: 0 }}>📜 Run History</h2>
              <div style={{ display: 'flex', gap: '10px' }}>
                <button style={S.btn('secondary')} onClick={loadAll}>Refresh</button>
                <button style={{ ...S.btn('danger'), fontSize: '12px', padding: '6px 12px' }} onClick={clearHistory}>
                  🗑️ Clear History
                </button>
              </div>
            </div>
            {history.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--muted-foreground)' }}>
                <p style={{ marginBottom: '1rem' }}>No runs yet.</p>
                <p style={{ fontSize: '0.875rem' }}>Run a model from the Models tab to see history here.</p>
                <button style={{ ...S.btn('primary'), marginTop: '1rem' }} onClick={loadAll}>🔄 Check Again</button>
              </div>
            ) : (
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead><tr style={{ background: 'var(--muted)' }}><th style={{ padding: '10px', textAlign: 'left', color: 'var(--muted-foreground)' }}>Time</th><th style={{ color: 'var(--muted-foreground)' }}>Model</th><th style={{ color: 'var(--muted-foreground)' }}>Universe</th><th style={{ color: 'var(--muted-foreground)' }}>Buy</th><th style={{ color: 'var(--muted-foreground)' }}>Sell</th><th style={{ color: 'var(--muted-foreground)' }}>Actions</th></tr></thead>
                <tbody>
                  {history.map(r => (
                    <tr key={r.id} style={{ borderBottom: '1px solid var(--border)' }}>
                      <td style={{ padding: '10px' }}>{new Date(r.run_timestamp).toLocaleString()}</td>
                      <td style={{ padding: '10px', fontWeight: 'bold' }}>{r.model_name}</td>
                      <td>{r.universe}</td>
                      <td style={{ textAlign: 'center', color: '#22c55e' }}>{r.buy_signals?.length || 0}</td>
                      <td style={{ textAlign: 'center', color: 'var(--destructive)' }}>{r.sell_signals?.length || 0}</td>
                      <td style={{ textAlign: 'center' }}><button style={S.btn('primary')} onClick={() => downloadPDF(r.id)}>📄 PDF</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {/* MODELS */}
        {tab === 'models' && (
          <>
            {!connected && <div style={{ ...S.card, background: 'var(--accent)', borderLeft: '4px solid var(--primary)', color: 'var(--accent-foreground)' }}><h3 style={{ margin: '0 0 0.5rem 0' }}>⚠️ Backend Not Connected</h3><p style={{ margin: 0 }}>Make sure the backend is running and accessible.</p></div>}
            {connected && (
              <>
                <h2>Technical Models ({models.filter(m => m.category === 'Technical').length})</h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '15px', marginBottom: '30px' }}>
                  {models.filter(m => m.category === 'Technical').map(m => <ModelCard key={m.id} model={m} result={results[m.id]} running={running === m.id} onRun={() => runModel(m.id)} onPDF={downloadPDF} onRunWithParams={(params) => runModelWithParams(m.id, params)} />)}
                </div>
                <h2 style={{ marginTop: '30px' }}>Fundamental Models ({models.filter(m => m.category === 'Fundamental').length})</h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '15px', marginBottom: '30px' }}>
                  {models.filter(m => m.category === 'Fundamental').map(m => <ModelCard key={m.id} model={m} result={results[m.id]} running={running === m.id} onRun={() => runModel(m.id)} onPDF={downloadPDF} onRunWithParams={(params) => runModelWithParams(m.id, params)} />)}
                </div>
                <h2 style={{ marginTop: '30px' }}>Quantitative Models ({models.filter(m => m.category === 'Quantitative').length})</h2>
                <p style={{ color: 'var(--muted-foreground)', marginBottom: '15px' }}>Statistical arbitrage and quantitative strategies</p>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '15px' }}>
                  {models.filter(m => m.category === 'Quantitative').map(m => <ModelCard key={m.id} model={m} result={results[m.id]} running={running === m.id} onRun={() => runModel(m.id)} onPDF={downloadPDF} onRunWithParams={(params) => runModelWithParams(m.id, params)} />)}
                </div>
              </>
            )}
          </>
        )}

        {/* UNIVERSE MANAGER */}
        {tab === 'universe' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div style={S.card}>
              <h3 style={{ marginTop: 0 }}>Create Custom Universe</h3>
              <input style={S.input} placeholder="Universe Name (e.g., My Watchlist)" value={newUni.name} onChange={e => setNewUni(p => ({ ...p, name: e.target.value }))} />
              <input style={S.input} placeholder="Description" value={newUni.desc} onChange={e => setNewUni(p => ({ ...p, desc: e.target.value }))} />
              <select style={{ ...S.select, width: '100%', marginBottom: '10px' }} value={newUni.market} onChange={e => setNewUni(p => ({ ...p, market: e.target.value }))}>
                <option value="US">US Market</option><option value="Thailand">Thailand (SET)</option><option value="Mixed">Mixed</option>
              </select>
              <textarea style={S.textarea} placeholder="Enter tickers (comma, space, or newline separated)&#10;e.g., AAPL, MSFT, GOOGL&#10;or PTT.BK AOT.BK KBANK.BK" value={newUni.tickers} onChange={e => { setNewUni(p => ({ ...p, tickers: e.target.value })); parseTickerText(); }} />
              <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
                <button style={{ ...S.btn('secondary'), fontSize: '12px', padding: '6px 12px' }} onClick={parseTickerText}>
                  🔍 Preview Tickers
                </button>
                <button style={S.btn('success')} onClick={createUniverse}>✨ Create Universe</button>
              </div>
              
              {parsePreview && (
                <div style={{ padding: '10px', background: 'var(--accent)', color: 'var(--accent-foreground)', borderRadius: 'var(--radius)', fontSize: '12px', marginTop: '10px' }}>
                  <strong>Preview:</strong> {parsePreview.tickers?.length || 0} tickers found
                  {parsePreview.tickers && parsePreview.tickers.length > 0 && (
                    <div style={{ marginTop: '5px', maxHeight: '100px', overflowY: 'auto' }}>
                      {parsePreview.tickers.slice(0, 20).join(', ')}
                      {parsePreview.tickers.length > 20 && ` ... and ${parsePreview.tickers.length - 20} more`}
                    </div>
                  )}
                </div>
              )}
            </div>
            <div style={S.card}>
              <h3 style={{ marginTop: 0 }}>Available Universes</h3>
              <h4>Built-in</h4>
              {universes.map(u => (
                <div key={u.id} style={{ padding: '8px', borderBottom: '1px solid var(--border)', cursor: 'pointer' }} onClick={() => loadUniverseDetails(u.id)}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div><b>{u.name}</b> ({u.count} stocks) - {u.market}</div>
                    <button style={{ ...S.btn('secondary'), fontSize: '11px', padding: '4px 8px' }} onClick={(e) => { e.stopPropagation(); loadUniverseDetails(u.id); }}>
                      View
                    </button>
                  </div>
                </div>
              ))}
              <h4 style={{ marginTop: '20px' }}>Custom</h4>
              {customUniverses.length === 0 ? (
                <p style={{ color: 'var(--muted-foreground)' }}>No custom universes yet</p>
              ) : (
                customUniverses.map(u => (
                  <div key={u.id} style={{ padding: '8px', borderBottom: '1px solid var(--border)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div><b>{u.name}</b> ({u.count} stocks) - {u.description}</div>
                      <div style={{ display: 'flex', gap: '5px' }}>
                        <button style={{ ...S.btn('secondary'), fontSize: '11px', padding: '4px 8px' }} onClick={() => setEditingUniverse(u)}>
                          ✏️ Edit
                        </button>
                        <button style={{ ...S.btn('danger'), fontSize: '11px', padding: '4px 8px' }} onClick={() => deleteCustomUniverse(u.id)}>
                          🗑️
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
            
            {/* Universe Details */}
            {selectedUniverseId && (
              <div style={{ ...S.card, gridColumn: '1 / -1' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                  <h3 style={{ margin: 0 }}>Universe Details: {universeDetails?.name || selectedUniverseId}</h3>
                  <button style={{ ...S.btn('secondary'), fontSize: '12px', padding: '6px 12px' }} onClick={() => { setSelectedUniverseId(null); setUniverseDetails(null); setUniverseStocks([]); }}>
                    ✕ Close
                  </button>
                </div>
                {universeDetails && (
                  <div style={{ marginBottom: '20px' }}>
                    <p><strong>Market:</strong> {universeDetails.market}</p>
                    <p><strong>Stock Count:</strong> {universeDetails.count || universeStocks.length}</p>
                  </div>
                )}
                {universeStocks.length > 0 && (
                  <div>
                    <h4>Stocks in Universe ({universeStocks.length})</h4>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', gap: '10px', maxHeight: '400px', overflowY: 'auto' }}>
                      {universeStocks.map((stock: any, i: number) => (
                        <div key={i} style={{ padding: '8px', background: 'var(--muted)', borderRadius: 'var(--radius)', cursor: 'pointer', transition: 'background 0.2s ease' }} onMouseEnter={(e) => e.currentTarget.style.background = 'var(--accent)'} onMouseLeave={(e) => e.currentTarget.style.background = 'var(--muted)'} onClick={() => loadStockDetails(stock.ticker)}>
                          <div style={{ fontWeight: 'bold' }}>{stock.ticker?.replace('.BK', '')}</div>
                          <div style={{ fontSize: '11px', color: 'var(--muted-foreground)' }}>{stock.name || stock.sector || ''}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
            
            {/* Stock Details */}
            {selectedStock && (
              <div style={{ ...S.card, gridColumn: '1 / -1' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                  <h3 style={{ margin: 0 }}>Stock Details: {selectedStock}</h3>
                  <button style={{ ...S.btn('secondary'), fontSize: '12px', padding: '6px 12px' }} onClick={() => { setSelectedStock(null); setStockDetails(null); }}>
                    ✕ Close
                  </button>
                </div>
                {stockDetails && (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
                    {Object.entries(stockDetails).map(([key, value]: [string, any]) => (
                      <div key={key} style={{ padding: '10px', background: 'var(--muted)', borderRadius: 'var(--radius)' }}>
                        <div style={{ fontSize: '11px', color: 'var(--muted-foreground)', marginBottom: '5px' }}>{key.replace(/_/g, ' ').toUpperCase()}</div>
                        <div style={{ fontWeight: 'bold' }}>{value || 'N/A'}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
            
            {/* Edit Custom Universe Modal */}
            {editingUniverse && (
              <div style={{ ...S.card, gridColumn: '1 / -1', background: 'var(--card)', border: '2px solid var(--primary)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                  <h3 style={{ margin: 0 }}>Edit Universe: {editingUniverse.name}</h3>
                  <button style={{ ...S.btn('secondary'), fontSize: '12px', padding: '6px 12px' }} onClick={() => setEditingUniverse(null)}>
                    ✕ Cancel
                  </button>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Name</label>
                    <input style={S.input} value={editingUniverse.name} onChange={e => setEditingUniverse({ ...editingUniverse, name: e.target.value })} />
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Market</label>
                    <select style={{ ...S.select, width: '100%' }} value={editingUniverse.market} onChange={e => setEditingUniverse({ ...editingUniverse, market: e.target.value })}>
                      <option value="US">US Market</option>
                      <option value="Thailand">Thailand (SET)</option>
                      <option value="Mixed">Mixed</option>
                    </select>
                  </div>
                </div>
                <div style={{ marginTop: '15px' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Description</label>
                  <input style={S.input} value={editingUniverse.description || ''} onChange={e => setEditingUniverse({ ...editingUniverse, description: e.target.value })} />
                </div>
                <div style={{ marginTop: '15px' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Tickers (comma-separated)</label>
                  <textarea style={S.textarea} value={editingUniverse.tickers?.join(', ') || ''} onChange={e => setEditingUniverse({ ...editingUniverse, tickers: e.target.value.split(',').map((t: string) => t.trim()).filter((t: string) => t) })} />
                </div>
                <div style={{ marginTop: '15px', display: 'flex', gap: '10px' }}>
                  <button style={S.btn('success')} onClick={() => updateCustomUniverse(editingUniverse.id, editingUniverse.name, editingUniverse.description || '', editingUniverse.tickers?.join(', ') || '', editingUniverse.market)}>
                    💾 Save Changes
                  </button>
                  <button style={S.btn('secondary')} onClick={() => setEditingUniverse(null)}>
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* BACKTEST */}
        {tab === 'backtest' && (
          <>
            <div style={S.card}>
              <h2 style={{ marginTop: 0 }}>📊 Model Backtesting</h2>
              <p style={{ color: 'var(--muted-foreground)', marginBottom: '20px' }}>Test model performance on historical data to identify which models actually work.</p>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Model</label>
                  <select style={{ ...S.select, width: '100%' }} value={backtestModel} onChange={e => setBacktestModel(e.target.value)}>
                    <option value="">Select a model...</option>
                    <optgroup label="Technical Models">
                      {models.filter(m => m.category === 'Technical').map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
                    </optgroup>
                    <optgroup label="Fundamental Models">
                      {models.filter(m => m.category === 'Fundamental').map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
                    </optgroup>
                  </select>
                </div>
                
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Universe</label>
                  <select style={{ ...S.select, width: '100%' }} value={backtestUniverse} onChange={e => setBacktestUniverse(e.target.value)}>
                    <optgroup label="Built-in">{universes.map(u => <option key={u.id} value={u.id}>{u.name}</option>)}</optgroup>
                    {customUniverses.length > 0 && <optgroup label="Custom">{customUniverses.map(u => <option key={u.id} value={u.id}>{u.name}</option>)}</optgroup>}
                  </select>
                </div>
                
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Initial Capital ($)</label>
                  <input type="number" style={S.input} value={backtestCapital} onChange={e => setBacktestCapital(Number(e.target.value))} min={1000} step={1000} />
                </div>
                
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Holding Period (days)</label>
                  <input type="number" style={S.input} value={backtestHoldingPeriod} onChange={e => setBacktestHoldingPeriod(Number(e.target.value))} min={1} max={252} />
                </div>
                
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Top N Signals</label>
                  <input type="number" style={S.input} value={backtestTopN} onChange={e => setBacktestTopN(Number(e.target.value))} min={1} max={50} />
                </div>
              </div>
              
              <div style={{ display: 'flex', gap: '10px' }}>
                <button 
                  style={{ ...S.btn('primary'), fontSize: '14px', padding: '10px 20px' }} 
                  onClick={runBacktest} 
                  disabled={!backtestModel || backtestRunning}
                >
                  {backtestRunning ? '⏳ Running Backtest...' : '▶ Run Backtest'}
                </button>
                {backtestModel && (
                  <button 
                    style={{ ...S.btn('secondary'), fontSize: '14px', padding: '10px 20px' }} 
                    onClick={async () => {
                      setBacktestRunning(true);
                      try {
                        log('info', `Running quick backtest for ${backtestModel}...`);
                        const r = await fetch(`${API_URL}/api/advanced/backtest/${backtestModel}?universe=${backtestUniverse}`);
                        if (r.ok) {
                          const d = await r.json();
                          setBacktestResults(d);
                          log('success', 'Quick backtest completed');
                        } else {
                          const e = await r.json();
                          log('error', `Quick backtest failed: ${e.detail || r.statusText}`);
                        }
                      } catch(e: any) {
                        log('error', `Quick backtest error: ${e.message || e}`);
                      }
                      setBacktestRunning(false);
                    }}
                    disabled={backtestRunning}
                  >
                    ⚡ Quick Backtest (Defaults)
                  </button>
                )}
              </div>
            </div>
            
            {backtestResults && (
              <div style={S.card}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '15px' }}>
                  <div>
                    <h3 style={{ marginTop: 0 }}>📈 Backtest Results: {backtestResults.model_name}</h3>
                    <p style={{ color: 'var(--muted-foreground)', fontSize: '12px', margin: 0 }}>Period: {backtestResults.period}</p>
                  </div>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button 
                      style={{ ...S.btn('primary'), fontSize: '12px', padding: '6px 12px' }} 
                      onClick={() => downloadBacktestPDF(backtestResults)}
                    >
                      📄 PDF
                    </button>
                    <button 
                      style={{ ...S.btn('success'), fontSize: '12px', padding: '6px 12px' }} 
                      onClick={() => downloadBacktestCSV(backtestResults)}
                    >
                      📊 CSV
                    </button>
                  </div>
                </div>
                
                {/* Performance Metrics */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginBottom: '30px' }}>
                  <div style={{ background: 'var(--muted)', padding: '15px', borderRadius: 'var(--radius)' }}>
                    <div style={{ fontSize: '11px', color: 'var(--muted-foreground)', marginBottom: '5px' }}>Total Return</div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: backtestResults.performance.total_return_pct >= 0 ? '#22c55e' : 'var(--destructive)' }}>
                      {backtestResults.performance.total_return_pct >= 0 ? '+' : ''}{backtestResults.performance.total_return_pct.toFixed(2)}%
                    </div>
                  </div>
                  
                  <div style={{ background: 'var(--muted)', padding: '15px', borderRadius: 'var(--radius)' }}>
                    <div style={{ fontSize: '11px', color: 'var(--muted-foreground)', marginBottom: '5px' }}>Annualized Return</div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: backtestResults.performance.annualized_return_pct >= 0 ? '#22c55e' : 'var(--destructive)' }}>
                      {backtestResults.performance.annualized_return_pct >= 0 ? '+' : ''}{backtestResults.performance.annualized_return_pct.toFixed(2)}%
                    </div>
                  </div>
                  
                  <div style={{ background: 'var(--muted)', padding: '15px', borderRadius: 'var(--radius)' }}>
                    <div style={{ fontSize: '11px', color: 'var(--muted-foreground)', marginBottom: '5px' }}>Sharpe Ratio</div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: backtestResults.performance.sharpe_ratio >= 1 ? '#22c55e' : backtestResults.performance.sharpe_ratio >= 0.5 ? '#f59e0b' : 'var(--destructive)' }}>
                      {backtestResults.performance.sharpe_ratio.toFixed(2)}
                    </div>
                  </div>
                  
                  <div style={{ background: 'var(--muted)', padding: '15px', borderRadius: 'var(--radius)' }}>
                    <div style={{ fontSize: '11px', color: 'var(--muted-foreground)', marginBottom: '5px' }}>Max Drawdown</div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--destructive)' }}>
                      {backtestResults.performance.max_drawdown_pct.toFixed(2)}%
                    </div>
                  </div>
                  
                  <div style={{ background: 'var(--muted)', padding: '15px', borderRadius: 'var(--radius)' }}>
                    <div style={{ fontSize: '11px', color: 'var(--muted-foreground)', marginBottom: '5px' }}>Final Value</div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
                      ${backtestResults.performance.final_value.toLocaleString()}
                    </div>
                  </div>
                </div>
                
                {/* Trade Statistics */}
                <h4 style={{ marginTop: '30px', marginBottom: '15px' }}>Trade Statistics</h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '15px', marginBottom: '30px' }}>
                  <div>
                    <div style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>Total Trades</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{backtestResults.trades.total}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>Win Rate</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: backtestResults.trades.win_rate_pct >= 50 ? '#22c55e' : 'var(--destructive)' }}>
                      {backtestResults.trades.win_rate_pct.toFixed(1)}%
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>Winning Trades</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#22c55e' }}>{backtestResults.trades.winning}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>Losing Trades</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: 'var(--destructive)' }}>{backtestResults.trades.losing}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>Avg Win</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#22c55e' }}>
                      +{backtestResults.trades.avg_win_pct.toFixed(2)}%
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>Avg Loss</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: 'var(--destructive)' }}>
                      {backtestResults.trades.avg_loss_pct.toFixed(2)}%
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>Profit Factor</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: backtestResults.trades.profit_factor >= 1.5 ? '#22c55e' : backtestResults.trades.profit_factor >= 1 ? '#f59e0b' : 'var(--destructive)' }}>
                      {backtestResults.trades.profit_factor.toFixed(2)}
                    </div>
                  </div>
                </div>
                
                {/* Recent Trades */}
                {backtestResults.recent_trades && backtestResults.recent_trades.length > 0 && (
                  <>
                    <h4 style={{ marginTop: '30px', marginBottom: '15px' }}>All Trades ({backtestResults.recent_trades.length} total)</h4>
                    <div style={{ overflowX: 'auto', maxHeight: '600px', overflowY: 'auto' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                        <thead style={{ position: 'sticky', top: 0, background: 'var(--muted)', zIndex: 1 }}>
                          <tr style={{ background: 'var(--muted)' }}>
                            <th style={{ padding: '8px', textAlign: 'left' }}>Entry</th>
                            <th style={{ padding: '8px', textAlign: 'left' }}>Exit</th>
                            <th style={{ padding: '8px', textAlign: 'left' }}>Ticker</th>
                            <th style={{ padding: '8px', textAlign: 'right' }}>Entry Price</th>
                            <th style={{ padding: '8px', textAlign: 'right' }}>Exit Price</th>
                            <th style={{ padding: '8px', textAlign: 'right' }}>Return</th>
                            <th style={{ padding: '8px', textAlign: 'right' }}>P&L</th>
                          </tr>
                        </thead>
                        <tbody>
                          {backtestResults.recent_trades.map((trade, i) => (
                            <tr key={i} style={{ borderBottom: '1px solid var(--border)' }}>
                              <td style={{ padding: '8px' }}>{new Date(trade.entry_date).toLocaleDateString()}</td>
                              <td style={{ padding: '8px' }}>{new Date(trade.exit_date).toLocaleDateString()}</td>
                              <td style={{ padding: '8px', fontWeight: 'bold' }}>{trade.ticker.replace('.BK', '')}</td>
                              <td style={{ padding: '8px', textAlign: 'right' }}>${trade.entry_price.toFixed(2)}</td>
                              <td style={{ padding: '8px', textAlign: 'right' }}>${trade.exit_price.toFixed(2)}</td>
                              <td style={{ padding: '8px', textAlign: 'right', color: trade.return_pct >= 0 ? '#22c55e' : 'var(--destructive)', fontWeight: 'bold' }}>
                                {trade.return_pct >= 0 ? '+' : ''}{trade.return_pct.toFixed(2)}%
                              </td>
                              <td style={{ padding: '8px', textAlign: 'right', color: trade.pnl >= 0 ? '#22c55e' : 'var(--destructive)', fontWeight: 'bold' }}>
                                {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </>
                )}
              </div>
            )}
          </>
        )}

        {/* ADVANCED FEATURES */}
        {tab === 'advanced' && (
          <>
            {/* Signal Combiner */}
            <div style={S.card}>
              <h2 style={{ marginTop: 0 }}>🔗 Signal Combiner</h2>
              <p style={{ color: 'var(--muted-foreground)', marginBottom: '20px' }}>Run multiple models and find stocks with confirmation from multiple signals. Higher confidence = better signals.</p>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '15px', marginBottom: '20px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Universe</label>
                  <select style={{ ...S.select, width: '100%' }} value={signalCombinerUniverse} onChange={e => setSignalCombinerUniverse(e.target.value)}>
                    <optgroup label="Built-in">{universes.map(u => <option key={u.id} value={u.id}>{u.name}</option>)}</optgroup>
                    {customUniverses.length > 0 && <optgroup label="Custom">{customUniverses.map(u => <option key={u.id} value={u.id}>{u.name}</option>)}</optgroup>}
                  </select>
                </div>
                
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Min Confirmation</label>
                  <input type="number" style={S.input} value={signalCombinerMinConf} onChange={e => setSignalCombinerMinConf(Number(e.target.value))} min={1} max={20} />
                  <small style={{ color: 'var(--muted-foreground)', fontSize: '11px' }}>How many models must agree</small>
                </div>
                
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Category (Optional)</label>
                  <select style={{ ...S.select, width: '100%' }} value={signalCombinerCategory} onChange={e => setSignalCombinerCategory(e.target.value)}>
                    <option value="">All Models</option>
                    <option value="technical">Technical Only</option>
                    <option value="fundamental">Fundamental Only</option>
                  </select>
                </div>
              </div>
              
              <button style={{ ...S.btn('primary') }} onClick={runSignalCombiner} disabled={signalCombinerRunning}>
                {signalCombinerRunning ? '⏳ Running...' : '▶ Run Signal Combiner'}
              </button>
              
              {signalCombinerResults && (
                <div style={{ marginTop: '20px', padding: '15px', background: 'var(--muted)', borderRadius: 'var(--radius)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                    <h4 style={{ marginTop: 0 }}>Results ({signalCombinerResults.total_models_analyzed || 0} models analyzed)</h4>
                    <button style={{ ...S.btn('primary'), fontSize: '12px', padding: '6px 12px' }} onClick={() => downloadSignalCombinerPDF(signalCombinerResults)}>
                      📄 Download PDF
                    </button>
                  </div>
                  
                  {signalCombinerResults.strong_buy_signals && signalCombinerResults.strong_buy_signals.length > 0 && (
                    <div style={{ marginBottom: '20px' }}>
                      <h5 style={{ color: '#22c55e', marginBottom: '10px' }}>🟢 Strong Buy Signals ({signalCombinerResults.strong_buy_signals.length})</h5>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '10px' }}>
                        {signalCombinerResults.strong_buy_signals.map((s: any, i: number) => (
                          <div key={i} style={{ background: 'white', padding: '10px', borderRadius: '5px', fontSize: '12px' }}>
                            <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>{s.ticker.replace('.BK', '')}</div>
                            <div style={{ color: 'var(--muted-foreground)' }}>{s.confirmations} confirmations • Score: {s.avg_score}</div>
                            <div style={{ fontSize: '11px', color: 'var(--muted-foreground)', marginTop: '3px' }}>{s.models?.join(', ')}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {signalCombinerResults.moderate_buy_signals && signalCombinerResults.moderate_buy_signals.length > 0 && (
                    <div style={{ marginBottom: '20px' }}>
                      <h5 style={{ color: '#ffc107', marginBottom: '10px' }}>🟡 Moderate Buy Signals ({signalCombinerResults.moderate_buy_signals.length})</h5>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '10px' }}>
                        {signalCombinerResults.moderate_buy_signals.slice(0, 10).map((s: any, i: number) => (
                          <div key={i} style={{ background: 'white', padding: '10px', borderRadius: '5px', fontSize: '12px' }}>
                            <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>{s.ticker.replace('.BK', '')}</div>
                            <div style={{ color: 'var(--muted-foreground)' }}>{s.confirmations} confirmations • Score: {s.avg_score}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {signalCombinerResults.strong_sell_signals && signalCombinerResults.strong_sell_signals.length > 0 && (
                    <div>
                      <h5 style={{ color: 'var(--destructive)', marginBottom: '10px' }}>🔴 Strong Sell Signals ({signalCombinerResults.strong_sell_signals.length})</h5>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '10px' }}>
                        {signalCombinerResults.strong_sell_signals.map((s: any, i: number) => (
                          <div key={i} style={{ background: 'white', padding: '10px', borderRadius: '5px', fontSize: '12px' }}>
                            <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>{s.ticker.replace('.BK', '')}</div>
                            <div style={{ color: 'var(--muted-foreground)' }}>{s.confirmations} confirmations • Score: {s.avg_score}</div>
                            <div style={{ fontSize: '11px', color: 'var(--muted-foreground)', marginTop: '3px' }}>{s.models?.join(', ')}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {(!signalCombinerResults.strong_buy_signals || signalCombinerResults.strong_buy_signals.length === 0) && 
                   (!signalCombinerResults.moderate_buy_signals || signalCombinerResults.moderate_buy_signals.length === 0) &&
                   (!signalCombinerResults.strong_sell_signals || signalCombinerResults.strong_sell_signals.length === 0) && (
                    <p style={{ color: 'var(--muted-foreground)', fontStyle: 'italic' }}>No signals found with the specified confirmation threshold. Try lowering the minimum confirmation.</p>
                  )}
                </div>
              )}
            </div>
            
            {/* Sector Rotation */}
            <div style={S.card}>
              <h2 style={{ marginTop: 0 }}>🔄 Sector Rotation</h2>
              <p style={{ color: 'var(--muted-foreground)', marginBottom: '20px' }}>Identify which sectors are strongest/weakest for rotation strategies.</p>
              
              <div style={{ display: 'flex', gap: '15px', marginBottom: '20px', alignItems: 'flex-end' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Universe</label>
                  <select style={{ ...S.select, width: '100%' }} value={sectorRotationUniverse} onChange={e => setSectorRotationUniverse(e.target.value)}>
                    <optgroup label="Built-in">{universes.map(u => <option key={u.id} value={u.id}>{u.name}</option>)}</optgroup>
                    {customUniverses.length > 0 && <optgroup label="Custom">{customUniverses.map(u => <option key={u.id} value={u.id}>{u.name}</option>)}</optgroup>}
                  </select>
                </div>
                <button style={{ ...S.btn('primary') }} onClick={runSectorRotation} disabled={sectorRotationRunning}>
                  {sectorRotationRunning ? '⏳ Analyzing...' : '▶ Analyze Sectors'}
                </button>
              </div>
              
              {sectorRotationResults && (
                <div style={{ marginTop: '20px' }}>
                  <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '15px' }}>
                    <button style={{ ...S.btn('primary'), fontSize: '12px', padding: '6px 12px' }} onClick={() => downloadSectorRotationPDF(sectorRotationResults)}>
                      📄 Download PDF
                    </button>
                  </div>
                  
                  {sectorRotationResults.rotation_recommendation && (
                    <div style={{ padding: '15px', background: '#e3f2fd', borderRadius: '8px', marginBottom: '20px' }}>
                      <h4 style={{ marginTop: 0 }}>💡 Rotation Recommendation</h4>
                      <p style={{ margin: '5px 0', fontWeight: 'bold' }}>{sectorRotationResults.rotation_recommendation.summary}</p>
                      <div style={{ marginTop: '10px', fontSize: '12px' }}>
                        <div><strong>Overweight:</strong> {sectorRotationResults.rotation_recommendation.overweight?.join(', ') || 'None'}</div>
                        <div><strong>Underweight:</strong> {sectorRotationResults.rotation_recommendation.underweight?.join(', ') || 'None'}</div>
                      </div>
                    </div>
                  )}
                  
                  {sectorRotationResults.sector_rankings && sectorRotationResults.sector_rankings.length > 0 && (
                    <div>
                      <h4>Sector Rankings</h4>
                      <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                          <thead>
                            <tr style={{ background: '#f8f9fa' }}>
                              <th style={{ padding: '8px', textAlign: 'left' }}>Rank</th>
                              <th style={{ padding: '8px', textAlign: 'left' }}>Sector</th>
                              <th style={{ padding: '8px', textAlign: 'right' }}>Momentum</th>
                              <th style={{ padding: '8px', textAlign: 'right' }}>1W Return</th>
                              <th style={{ padding: '8px', textAlign: 'right' }}>1M Return</th>
                              <th style={{ padding: '8px', textAlign: 'right' }}>3M Return</th>
                              <th style={{ padding: '8px', textAlign: 'center' }}>Signal</th>
                            </tr>
                          </thead>
                          <tbody>
                            {sectorRotationResults.sector_rankings.map((s: any, i: number) => (
                              <tr key={i} style={{ borderBottom: '1px solid var(--border)' }}>
                                <td style={{ padding: '8px', fontWeight: 'bold' }}>#{s.rank}</td>
                                <td style={{ padding: '8px', fontWeight: 'bold' }}>{s.sector}</td>
                                <td style={{ padding: '8px', textAlign: 'right' }}>{s.momentum_score.toFixed(2)}</td>
                                <td style={{ padding: '8px', textAlign: 'right', color: s.return_1w >= 0 ? '#22c55e' : 'var(--destructive)' }}>
                                  {s.return_1w >= 0 ? '+' : ''}{s.return_1w.toFixed(2)}%
                                </td>
                                <td style={{ padding: '8px', textAlign: 'right', color: s.return_1m >= 0 ? '#22c55e' : 'var(--destructive)' }}>
                                  {s.return_1m >= 0 ? '+' : ''}{s.return_1m.toFixed(2)}%
                                </td>
                                <td style={{ padding: '8px', textAlign: 'right', color: s.return_3m >= 0 ? '#22c55e' : 'var(--destructive)' }}>
                                  {s.return_3m >= 0 ? '+' : ''}{s.return_3m.toFixed(2)}%
                                </td>
                                <td style={{ padding: '8px', textAlign: 'center' }}>
                                  <span style={{
                                    padding: '3px 8px',
                                    borderRadius: '3px',
                                    background: s.signal === 'BUY' ? '#28a745' : s.signal === 'SELL' ? '#dc3545' : '#ffc107',
                                    color: 'white',
                                    fontSize: '11px',
                                    fontWeight: 'bold'
                                  }}>
                                    {s.signal}
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
            
            {/* Market Regime Detection */}
            <div style={S.card}>
              <h2 style={{ marginTop: 0 }}>📊 Market Regime Detection</h2>
              <p style={{ color: 'var(--muted-foreground)', marginBottom: '20px' }}>Identify current market conditions (Bull/Bear/Neutral) to adjust your strategy accordingly.</p>
              
              <div style={{ display: 'flex', gap: '15px', marginBottom: '20px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Index</label>
                  <select style={{ ...S.select, width: '150px' }} value={marketRegimeIndex} onChange={e => setMarketRegimeIndex(e.target.value)}>
                    <option value="SPY">SPY (S&P 500)</option>
                    <option value="QQQ">QQQ (Nasdaq)</option>
                    <option value="IWM">IWM (Russell 2000)</option>
                    <option value="DIA">DIA (Dow Jones)</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold' }}>Universe</label>
                  <select style={{ ...S.select, width: '150px' }} value={marketRegimeUniverse} onChange={e => setMarketRegimeUniverse(e.target.value)}>
                    <optgroup label="Built-in">{universes.map(u => <option key={u.id} value={u.id}>{u.name}</option>)}</optgroup>
                  </select>
                </div>
                <button style={{ ...S.btn('primary') }} onClick={runMarketRegime} disabled={marketRegimeRunning}>
                  {marketRegimeRunning ? '⏳ Detecting...' : '▶ Detect Regime'}
                </button>
              </div>
              
              {marketRegimeResults && (
                <div style={{ marginTop: '20px' }}>
                  {/* Regime Badge */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '20px' }}>
                    <div style={{
                      padding: '15px 30px',
                      borderRadius: '10px',
                      background: marketRegimeResults.regime === 'BULL' ? '#22c55e' : marketRegimeResults.regime === 'BEAR' ? '#ef4444' : '#f59e0b',
                      color: 'white',
                      fontSize: '24px',
                      fontWeight: 'bold'
                    }}>
                      {marketRegimeResults.regime === 'BULL' ? '🐂' : marketRegimeResults.regime === 'BEAR' ? '🐻' : '➡️'} {marketRegimeResults.regime}
                    </div>
                    <div>
                      <div style={{ fontSize: '14px', color: 'var(--muted-foreground)' }}>Volatility Regime</div>
                      <div style={{ fontSize: '18px', fontWeight: 'bold', color: marketRegimeResults.volatility_regime === 'HIGH' ? '#ef4444' : marketRegimeResults.volatility_regime === 'LOW' ? '#22c55e' : '#f59e0b' }}>
                        {marketRegimeResults.volatility_regime}
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: '14px', color: 'var(--muted-foreground)' }}>Risk Level</div>
                      <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{marketRegimeResults.risk_level}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '14px', color: 'var(--muted-foreground)' }}>Recommended Exposure</div>
                      <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#3b82f6' }}>{marketRegimeResults.recommended_exposure}%</div>
                    </div>
                  </div>
                  
                  {/* Recommendation */}
                  {marketRegimeResults.recommendation && (
                    <div style={{ padding: '15px', background: 'var(--accent)', borderRadius: 'var(--radius)', marginBottom: '15px' }}>
                      <h4 style={{ margin: '0 0 10px 0' }}>💡 Recommendation</h4>
                      <p style={{ margin: 0 }}>{marketRegimeResults.recommendation}</p>
                    </div>
                  )}
                  
                  {/* Signals Grid */}
                  {marketRegimeResults.signals && (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '10px', marginTop: '15px' }}>
                      {Object.entries(marketRegimeResults.signals).map(([key, value]: [string, any]) => (
                        <div key={key} style={{ padding: '10px', background: 'var(--muted)', borderRadius: 'var(--radius)', textAlign: 'center' }}>
                          <div style={{ fontSize: '11px', color: 'var(--muted-foreground)', marginBottom: '5px' }}>{key.replace(/_/g, ' ')}</div>
                          <div style={{ fontSize: '16px', fontWeight: 'bold', color: value ? '#22c55e' : '#ef4444' }}>
                            {typeof value === 'boolean' ? (value ? '✓' : '✗') : value}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
            
            {/* Scheduled Scans */}
            <div style={S.card}>
              <h2 style={{ marginTop: 0 }}>⏰ Scheduled Scans</h2>
              <p style={{ color: 'var(--muted-foreground)', marginBottom: '20px' }}>Set up automatic daily scans to run models at specific times.</p>
              
              {/* Create New Scan */}
              <div style={{ background: 'var(--muted)', padding: '15px', borderRadius: 'var(--radius)', marginBottom: '20px' }}>
                <h4 style={{ margin: '0 0 15px 0' }}>Create New Scheduled Scan</h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '15px', marginBottom: '15px' }}>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px', fontWeight: 'bold' }}>Model</label>
                    <select style={{ ...S.select, width: '100%' }} value={newScanModel} onChange={e => setNewScanModel(e.target.value)}>
                      <option value="">Select model...</option>
                      <optgroup label="Technical">
                        {models.filter(m => m.category === 'Technical').map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
                      </optgroup>
                      <optgroup label="Fundamental">
                        {models.filter(m => m.category === 'Fundamental').map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
                      </optgroup>
                      <optgroup label="Quantitative">
                        {models.filter(m => m.category === 'Quantitative').map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
                      </optgroup>
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px', fontWeight: 'bold' }}>Universe</label>
                    <select style={{ ...S.select, width: '100%' }} value={newScanUniverse} onChange={e => setNewScanUniverse(e.target.value)}>
                      <optgroup label="Built-in">{universes.map(u => <option key={u.id} value={u.id}>{u.name}</option>)}</optgroup>
                      {customUniverses.length > 0 && <optgroup label="Custom">{customUniverses.map(u => <option key={u.id} value={u.id}>{u.name}</option>)}</optgroup>}
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px', fontWeight: 'bold' }}>Time (Market Hours)</label>
                    <input type="time" style={{ ...S.input, marginBottom: 0 }} value={newScanTime} onChange={e => setNewScanTime(e.target.value)} />
                  </div>
                </div>
                <div style={{ marginBottom: '15px' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px', fontWeight: 'bold' }}>Days</label>
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                    {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(day => (
                      <button
                        key={day}
                        style={{
                          padding: '5px 10px',
                          borderRadius: 'var(--radius)',
                          border: '1px solid var(--border)',
                          background: newScanDays.includes(day) ? 'var(--primary)' : 'transparent',
                          color: newScanDays.includes(day) ? 'white' : 'var(--foreground)',
                          cursor: 'pointer',
                          fontSize: '12px'
                        }}
                        onClick={() => {
                          if (newScanDays.includes(day)) {
                            setNewScanDays(newScanDays.filter(d => d !== day));
                          } else {
                            setNewScanDays([...newScanDays, day]);
                          }
                        }}
                      >
                        {day}
                      </button>
                    ))}
                  </div>
                </div>
                <button style={S.btn('success')} onClick={createScheduledScan}>
                  ➕ Create Scheduled Scan
                </button>
              </div>
              
              {/* Existing Scans */}
              <h4>Active Scans ({scheduledScans.length})</h4>
              {scheduledScans.length === 0 ? (
                <p style={{ color: 'var(--muted-foreground)', fontStyle: 'italic' }}>No scheduled scans yet. Create one above to automate your daily analysis.</p>
              ) : (
                <div style={{ display: 'grid', gap: '10px' }}>
                  {scheduledScans.map((scan: any) => (
                    <div key={scan.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', background: 'var(--muted)', borderRadius: 'var(--radius)' }}>
                      <div>
                        <div style={{ fontWeight: 'bold' }}>{scan.model_name || scan.model_id}</div>
                        <div style={{ fontSize: '12px', color: 'var(--muted-foreground)' }}>
                          {scan.universe} • {scan.schedule_time} • {scan.days?.join(', ')}
                        </div>
                      </div>
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                        <button
                          style={{
                            padding: '5px 10px',
                            borderRadius: 'var(--radius)',
                            border: 'none',
                            background: scan.enabled ? '#22c55e' : 'var(--muted-foreground)',
                            color: 'white',
                            cursor: 'pointer',
                            fontSize: '11px'
                          }}
                          onClick={() => toggleScheduledScan(scan.id, !scan.enabled)}
                        >
                          {scan.enabled ? 'ON' : 'OFF'}
                        </button>
                        <button style={{ ...S.btn('danger'), fontSize: '11px', padding: '5px 10px' }} onClick={() => deleteScheduledScan(scan.id)}>
                          🗑️
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            
          </>
        )}

        {/* STATUS */}
        {tab === 'status' && (
          <>
            <div style={S.card}>
              <h3 style={{ marginTop: 0 }}>🔌 Connection</h3>
              <p><span style={S.dot(connected)} /> {connected ? 'Connected to backend' : 'Not connected'}</p>
              <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                <button style={S.btn('primary')} onClick={checkConn}>Test Connection</button>
                <button style={S.btn('secondary')} onClick={loadAll}>Reload All Data</button>
                <button style={S.btn('secondary')} onClick={testDataFetch}>🧪 Test Data Fetch</button>
                <button style={S.btn('secondary')} onClick={clearCache}>🗑️ Clear Cache</button>
                <button style={S.btn('secondary')} onClick={loadStatusLogs}>📋 Load System Logs</button>
              </div>
            </div>
            <div style={S.card}>
              <h3 style={{ marginTop: 0 }}>📋 Application Logs ({logs.length})</h3>
              <div style={{ maxHeight: '300px', overflow: 'auto', fontFamily: 'var(--font-mono)', fontSize: '0.75rem', borderRadius: 'var(--radius)', background: 'var(--muted)', padding: '0.5rem' }}>
                {logs.slice().reverse().map((l, i) => (
                  <div key={i} style={{ 
                    padding: '0.5rem', 
                    borderLeft: `3px solid ${l.type === 'error' ? 'var(--destructive)' : l.type === 'success' ? '#22c55e' : 'var(--primary)'}`, 
                    background: l.type === 'error' ? 'rgba(239, 68, 68, 0.1)' : l.type === 'success' ? 'rgba(34, 197, 94, 0.1)' : 'rgba(59, 130, 246, 0.1)', 
                    marginBottom: '0.375rem',
                    borderRadius: 'var(--radius)',
                    color: 'var(--foreground)'
                  }}>
                    <span style={{ color: 'var(--muted-foreground)', marginRight: '0.5rem' }}>[{l.time}]</span>
                    <span style={{ color: l.type === 'error' ? 'var(--destructive)' : l.type === 'success' ? '#22c55e' : 'var(--foreground)' }}>{l.message}</span>
                  </div>
                ))}
              </div>
              <button style={{ ...S.btn('secondary'), marginTop: '10px' }} onClick={() => setLogs([])}>Clear</button>
            </div>
            <div style={S.card}>
              <h3 style={{ marginTop: 0, marginBottom: '1rem' }}>🔧 Troubleshooting</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
                  <span style={{ color: 'var(--primary)', fontWeight: '600', minWidth: '1.5rem' }}>1.</span>
                  <div style={{ flex: 1, color: 'var(--foreground)' }}>
                    Open terminal in <code style={{ background: 'var(--muted)', padding: '0.125rem 0.375rem', borderRadius: 'var(--radius)', fontFamily: 'var(--font-mono)', fontSize: '0.875rem', color: 'var(--foreground)' }}>backend</code> folder
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
                  <span style={{ color: 'var(--primary)', fontWeight: '600', minWidth: '1.5rem' }}>2.</span>
                  <div style={{ flex: 1, color: 'var(--foreground)' }}>
                    Run: <code style={{ background: 'var(--muted)', padding: '0.125rem 0.375rem', borderRadius: 'var(--radius)', fontFamily: 'var(--font-mono)', fontSize: '0.875rem', color: 'var(--foreground)' }}>pip install -r requirements.txt</code>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
                  <span style={{ color: 'var(--primary)', fontWeight: '600', minWidth: '1.5rem' }}>3.</span>
                  <div style={{ flex: 1, color: 'var(--foreground)' }}>
                    Run: <code style={{ background: 'var(--muted)', padding: '0.125rem 0.375rem', borderRadius: 'var(--radius)', fontFamily: 'var(--font-mono)', fontSize: '0.875rem', color: 'var(--foreground)' }}>uvicorn app.main:app --reload --port 8000</code>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
                  <span style={{ color: 'var(--primary)', fontWeight: '600', minWidth: '1.5rem' }}>4.</span>
                  <div style={{ flex: 1, color: 'var(--foreground)' }}>
                    Test: <a href="http://localhost:8000/health" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary)', textDecoration: 'none', borderBottom: '1px solid var(--primary)', transition: 'opacity 0.2s ease' }} onMouseEnter={(e) => e.currentTarget.style.opacity = '0.8'} onMouseLeave={(e) => e.currentTarget.style.opacity = '1'}>http://localhost:8000/health</a>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}

        {/* MODEL DETAIL */}
        {tab === 'model-detail' && (
          <>
            <div style={S.card}>
              <h2 style={{ marginTop: 0 }}>📖 Model Documentation</h2>
              <p style={{ color: 'var(--muted-foreground)', marginBottom: '1rem' }}>Select a model to view detailed documentation, parameters, and usage instructions.</p>
              
              {Object.keys(modelDocs).length === 0 ? (
                <p style={{ color: 'var(--muted-foreground)' }}>Loading model documentation...</p>
              ) : (
                <>
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500' }}>Select Model:</label>
                    <select 
                      style={{ ...S.select, width: '100%', maxWidth: '400px' }} 
                      value={selDoc || ''} 
                      onChange={e => setSelDoc(e.target.value || null)}
                    >
                      <option value="">-- Select a model --</option>
                      {Object.entries(modelDocs).map(([id, doc]: [string, any]) => (
                        <option key={id} value={id}>{doc.name || id} ({doc.category || 'Unknown'})</option>
                      ))}
                    </select>
                  </div>

                  {selDoc && modelDocs[selDoc] && (
                    <div style={{ borderTop: '1px solid var(--border)', paddingTop: '1rem', marginTop: '1rem' }}>
                      {(() => {
                        const doc = modelDocs[selDoc];
                        return (
                          <>
                            <div style={{ marginBottom: '1rem' }}>
                              <h3 style={{ margin: '0 0 0.5rem 0', color: 'var(--foreground)' }}>{doc.name || selDoc}</h3>
                              <span style={{ 
                                fontSize: '0.75rem', 
                                padding: '0.25rem 0.5rem', 
                                borderRadius: 'var(--radius)', 
                                background: doc.category === 'Technical' ? 'var(--accent)' : 'var(--muted)', 
                                color: doc.category === 'Technical' ? 'var(--accent-foreground)' : 'var(--muted-foreground)'
                              }}>
                                {doc.category || 'Unknown'}
                              </span>
                            </div>

                            {doc.summary && (
                              <div style={{ marginBottom: '1rem' }}>
                                <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', fontWeight: '600', color: 'var(--foreground)' }}>Summary</h4>
                                <p style={{ color: 'var(--muted-foreground)', margin: 0, lineHeight: '1.6' }}>{cleanMarkdown(doc.summary)}</p>
                              </div>
                            )}

                            {doc.description && (
                              <div style={{ marginBottom: '1rem' }}>
                                <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', fontWeight: '600', color: 'var(--foreground)' }}>Description</h4>
                                <p style={{ color: 'var(--muted-foreground)', margin: 0, lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>{cleanMarkdown(doc.description)}</p>
                              </div>
                            )}

                            {doc.parameters && Object.keys(doc.parameters).length > 0 && (
                              <div style={{ marginBottom: '1rem' }}>
                                <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', fontWeight: '600', color: 'var(--foreground)' }}>Parameters</h4>
                                <div style={{ background: 'var(--muted)', borderRadius: 'var(--radius)', padding: '0.75rem' }}>
                                  {Object.entries(doc.parameters).map(([key, param]: [string, any]) => (
                                    <div key={key} style={{ marginBottom: '0.5rem', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border)' }}>
                                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.25rem' }}>
                                        <code style={{ background: 'var(--background)', padding: '0.125rem 0.375rem', borderRadius: 'var(--radius)', fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--foreground)' }}>{key}</code>
                                        {param.default !== undefined && (
                                          <span style={{ fontSize: '0.75rem', color: 'var(--muted-foreground)' }}>Default: {String(param.default)}</span>
                                        )}
                                      </div>
                                      {param.description && (
                                        <p style={{ fontSize: '0.75rem', color: 'var(--muted-foreground)', margin: 0 }}>{cleanMarkdown(String(param.description))}</p>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {doc.signals && (
                              <div style={{ marginBottom: '1rem' }}>
                                <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', fontWeight: '600', color: 'var(--foreground)' }}>Signals</h4>
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
                                  {doc.signals.buy && (
                                    <div style={{ background: 'rgba(34, 197, 94, 0.1)', border: '1px solid #22c55e', borderRadius: 'var(--radius)', padding: '0.75rem' }}>
                                      <div style={{ fontSize: '0.75rem', fontWeight: '600', color: '#22c55e', marginBottom: '0.25rem' }}>🟢 Buy Signal</div>
                                      <p style={{ fontSize: '0.75rem', color: 'var(--foreground)', margin: 0 }}>{cleanMarkdown(doc.signals.buy)}</p>
                                    </div>
                                  )}
                                  {doc.signals.sell && (
                                    <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid var(--destructive)', borderRadius: 'var(--radius)', padding: '0.75rem' }}>
                                      <div style={{ fontSize: '0.75rem', fontWeight: '600', color: 'var(--destructive)', marginBottom: '0.25rem' }}>🔴 Sell Signal</div>
                                      <p style={{ fontSize: '0.75rem', color: 'var(--foreground)', margin: 0 }}>{cleanMarkdown(doc.signals.sell)}</p>
                                    </div>
                                  )}
                                </div>
                              </div>
                            )}

                            {doc.references && doc.references.length > 0 && (
                              <div style={{ marginBottom: '1rem' }}>
                                <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', fontWeight: '600', color: 'var(--foreground)' }}>References</h4>
                                <ul style={{ margin: 0, paddingLeft: '1.25rem', color: 'var(--muted-foreground)', fontSize: '0.875rem' }}>
                                  {doc.references.map((ref: string, i: number) => (
                                    <li key={i} style={{ marginBottom: '0.25rem' }}>{ref}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </>
                        );
                      })()}
                    </div>
                  )}
                </>
              )}
            </div>
          </>
        )}

        {/* SETTINGS */}
        {tab === 'settings' && (
          <>
            <div style={S.card}>
              <h2 style={{ marginTop: 0 }}>⚙️ Settings</h2>
              <p style={{ color: 'var(--muted-foreground)', marginBottom: '1.5rem' }}>Configure application preferences and default values.</p>
              
              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: 'var(--foreground)' }}>
                  Top N Signals
                </label>
                <p style={{ fontSize: '0.75rem', color: 'var(--muted-foreground)', margin: '0 0 0.75rem 0' }}>
                  Number of top signals to display when running models (default: 10)
                </p>
                <select 
                  style={{ ...S.select, background: 'var(--background)', maxWidth: '200px' }} 
                  value={topN} 
                  onChange={e => setTopN(Number(e.target.value))}
                >
                  <option value={5}>5</option>
                  <option value={10}>10</option>
                  <option value={20}>20</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                </select>
              </div>

              <div style={{ borderTop: '1px solid var(--border)', paddingTop: '1rem', marginTop: '1rem' }}>
                <h3 style={{ margin: '0 0 0.75rem 0', fontSize: '1rem', fontWeight: '600' }}>Current Configuration</h3>
                <div style={{ background: 'var(--muted)', borderRadius: 'var(--radius)', padding: '0.75rem', fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
                  <div style={{ marginBottom: '0.5rem' }}>
                    <span style={{ color: 'var(--muted-foreground)' }}>Top N Signals:</span>{' '}
                    <span style={{ color: 'var(--foreground)', fontWeight: '600' }}>{topN}</span>
                  </div>
                  <div style={{ marginBottom: '0.5rem' }}>
                    <span style={{ color: 'var(--muted-foreground)' }}>Default Universe:</span>{' '}
                    <span style={{ color: 'var(--foreground)', fontWeight: '600' }}>{universe}</span>
                  </div>
                  <div>
                    <span style={{ color: 'var(--muted-foreground)' }}>Backend Status:</span>{' '}
                    <span style={{ color: connected ? '#22c55e' : 'var(--destructive)', fontWeight: '600' }}>
                      {connected ? 'Connected' : 'Disconnected'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

// Model Card Component with Parameter Customization
function ModelCard({ model, result, running, onRun, onPDF, onRunWithParams }: { 
  model: Model; 
  result?: ModelResult; 
  running: boolean; 
  onRun: () => void; 
  onPDF: (id: string) => void;
  onRunWithParams?: (params: Record<string, any>) => void;
}) {
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
          <h3 style={{ margin: 0 }}>{model.name}</h3>
          <span style={{ fontSize: '11px', padding: '2px 6px', borderRadius: 'var(--radius)', background: catStyle.bg, color: catStyle.color }}>{model.category}</span>
        </div>
        <div style={{ display: 'flex', gap: '5px' }}>
          <button style={{ ...S.btn('secondary'), fontSize: '11px', padding: '4px 8px' }} onClick={() => setShowParams(!showParams)} title="Customize Parameters">⚙️</button>
          <button style={{ ...S.btn('primary'), opacity: running ? 0.6 : 1 }} onClick={onRun} disabled={running}>{running ? '⏳...' : '▶ Run'}</button>
        </div>
      </div>
      <p style={{ color: 'var(--muted-foreground)', fontSize: '12px', margin: '10px 0' }}>{model.description}</p>
      
      {/* Parameter Customization Panel */}
      {showParams && model.default_parameters && (
        <div style={{ background: 'var(--muted)', padding: '12px', borderRadius: 'var(--radius)', marginBottom: '10px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
            <h4 style={{ margin: 0, fontSize: '13px' }}>⚙️ Custom Parameters</h4>
            <button style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '14px' }} onClick={() => setShowParams(false)}>✕</button>
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
            <button style={{ ...S.btn('success'), fontSize: '11px', padding: '6px 12px' }} onClick={runWithCustomParams} disabled={running}>
              {running ? '⏳...' : '▶ Run with Custom'}
            </button>
            <button style={{ ...S.btn('secondary'), fontSize: '11px', padding: '6px 12px' }} onClick={() => setCustomParams(model.default_parameters || {})}>
              Reset
            </button>
          </div>
        </div>
      )}
      
      {result && (
        <div style={{ borderTop: '1px solid var(--border)', paddingTop: '10px' }}>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '8px', fontSize: '12px', flexWrap: 'wrap' }}>
            <span style={{ color: '#22c55e' }}>✅ {result.buy_signals.length} Buy</span>
            <span style={{ color: 'var(--destructive)' }}>🔻 {result.sell_signals.length} Sell</span>
            <span style={{ color: 'var(--muted-foreground)' }}>{result.stocks_with_data}/{result.total_stocks_analyzed} stocks</span>
            <span style={{ color: 'var(--muted-foreground)', fontSize: '11px', fontStyle: 'italic' }}>(Top signals shown)</span>
          </div>
          {result.buy_signals.slice(0, 4).map((s, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', padding: '3px 0' }}>
              <b>{s.ticker.replace('.BK', '')}</b><span>${s.price_at_signal.toFixed(2)}</span><span style={{ color: '#22c55e' }}>{s.score.toFixed(0)}</span>
            </div>
          ))}
          <button style={{ ...S.btn('secondary'), marginTop: '8px', fontSize: '11px' }} onClick={() => onPDF(result.run_id)}>📄 Download PDF</button>
        </div>
      )}
    </div>
  );
}
