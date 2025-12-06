'use client';

import { useState, useEffect } from 'react';

// API URL - can be overridden by environment variable
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Types
interface Signal { ticker: string; signal_type: string; score: number; price_at_signal: number; }
interface Model { id: string; name: string; description: string; category: string; }
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

const S = {
  card: { background: 'white', borderRadius: '8px', padding: '20px', marginBottom: '15px', boxShadow: '0 2px 4px rgba(0,0,0,0.08)' } as React.CSSProperties,
  btn: (v: string) => ({ padding: '8px 16px', background: v === 'primary' ? '#4a90d9' : v === 'success' ? '#28a745' : v === 'danger' ? '#dc3545' : '#e0e0e0', color: v === 'primary' || v === 'success' || v === 'danger' ? 'white' : '#333', border: 'none', borderRadius: '5px', cursor: 'pointer', marginRight: '8px', fontSize: '13px' }),
  select: { padding: '8px 12px', borderRadius: '5px', border: '1px solid #ddd', marginRight: '10px', fontSize: '13px' } as React.CSSProperties,
  tab: (a: boolean) => ({ padding: '8px 16px', background: a ? '#4a90d9' : 'transparent', color: a ? 'white' : '#666', border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: a ? 'bold' : 'normal' as const, fontSize: '14px' }),
  dot: (ok: boolean) => ({ width: '10px', height: '10px', borderRadius: '50%', background: ok ? '#28a745' : '#dc3545', display: 'inline-block', marginRight: '8px' }),
  input: { padding: '8px 12px', borderRadius: '5px', border: '1px solid #ddd', width: '100%', marginBottom: '10px', fontSize: '13px' } as React.CSSProperties,
  textarea: { padding: '8px 12px', borderRadius: '5px', border: '1px solid #ddd', width: '100%', minHeight: '100px', marginBottom: '10px', fontSize: '13px', fontFamily: 'monospace' } as React.CSSProperties,
};

export default function Home() {
  const [tab, setTab] = useState<'history'|'models'|'universe'|'backtest'|'advanced'|'status'>('models');
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
    try { const r = await fetch(`${API_URL}/api/models/history`); if (r.ok) { const d = await r.json(); setHistory(d.runs || []); } } catch(e) {}
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


  return (
    <div style={{ fontFamily: 'system-ui', minHeight: '100vh', background: '#f5f5f5' }}>
      {/* Header */}
      <div style={{ background: '#1a1a2e', color: 'white', padding: '15px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div><h1 style={{ margin: 0, fontSize: '20px' }}>📈 Quant Stock Analysis v2</h1></div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <span style={S.dot(connected)} />
          <select style={{ ...S.select, background: 'white' }} value={universe} onChange={e => setUniverse(e.target.value)}>
            <optgroup label="Built-in">{universes.map(u => <option key={u.id} value={u.id}>{u.name} ({u.count})</option>)}</optgroup>
            {customUniverses.length > 0 && <optgroup label="Custom">{customUniverses.map(u => <option key={u.id} value={u.id}>{u.name} ({u.count})</option>)}</optgroup>}
          </select>
          <label style={{ fontSize: '12px', color: 'white', display: 'flex', alignItems: 'center', gap: '5px' }}>
            Top N:
            <select style={{ ...S.select, background: 'white', padding: '4px 8px', fontSize: '12px' }} value={topN} onChange={e => setTopN(Number(e.target.value))}>
              <option value={5}>5</option>
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </label>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '5px', background: '#fff', padding: '10px 20px', borderBottom: '1px solid #e0e0e0', flexWrap: 'wrap' }}>
        {(['history', 'models', 'universe', 'backtest', 'advanced', 'status'] as const).map(t => (
          <button key={t} style={S.tab(tab === t)} onClick={() => setTab(t)}>
            {t === 'history' ? '📜 History' : t === 'models' ? '📚 Models' : t === 'universe' ? '🌐 Universe' : t === 'backtest' ? '📊 Backtest' : t === 'advanced' ? '⚡ Advanced' : '🔧 Status'}
          </button>
        ))}
      </div>

      <div style={{ padding: '20px' }}>
        {/* Connection Warning */}
        {!connected && <div style={{ ...S.card, background: '#fff3cd', borderLeft: '4px solid #ffc107' }}><h3>⚠️ Backend Not Connected</h3><p>Make sure the backend is running and accessible.</p></div>}

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
            {history.length === 0 ? <p>No runs yet.</p> : (
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead><tr style={{ background: '#f8f9fa' }}><th style={{ padding: '10px', textAlign: 'left' }}>Time</th><th>Model</th><th>Universe</th><th>Buy</th><th>Sell</th><th>Actions</th></tr></thead>
                <tbody>
                  {history.map(r => (
                    <tr key={r.id} style={{ borderBottom: '1px solid #eee' }}>
                      <td style={{ padding: '10px' }}>{new Date(r.run_timestamp).toLocaleString()}</td>
                      <td style={{ padding: '10px', fontWeight: 'bold' }}>{r.model_name}</td>
                      <td>{r.universe}</td>
                      <td style={{ textAlign: 'center', color: '#28a745' }}>{r.buy_signals?.length || 0}</td>
                      <td style={{ textAlign: 'center', color: '#dc3545' }}>{r.sell_signals?.length || 0}</td>
                      <td style={{ textAlign: 'center' }}><button style={S.btn('primary')} onClick={() => downloadPDF(r.id)}>📄 PDF</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {/* MODELS DOCUMENTATION */}
        {tab === 'models' && (
          <div style={{ display: 'grid', gridTemplateColumns: '220px 1fr', gap: '20px' }}>
            <div style={S.card}>
              <h3 style={{ marginTop: 0 }}>Models</h3>
              {Object.entries(modelDocs).map(([id, doc]: [string, any]) => (
                <div key={id} onClick={() => setSelDoc(id)} style={{ padding: '8px', borderRadius: '5px', cursor: 'pointer', background: selDoc === id ? '#e3f2fd' : 'transparent', marginBottom: '4px' }}>
                  <div style={{ fontWeight: 'bold', fontSize: '13px' }}>{doc.name}</div>
                  <div style={{ fontSize: '11px', color: '#666' }}>{doc.category}</div>
                </div>
              ))}
            </div>
            <div style={S.card}>
              {selDoc && modelDocs[selDoc] ? (
                <>
                  <h2 style={{ marginTop: 0 }}>{modelDocs[selDoc].name}</h2>
                  <span style={{ background: modelDocs[selDoc].category === 'Technical' ? '#cce5ff' : '#e2d5f1', padding: '4px 10px', borderRadius: '4px', fontSize: '12px' }}>{modelDocs[selDoc].category}</span>
                  <p style={{ marginTop: '15px', fontStyle: 'italic', color: '#666' }}>{modelDocs[selDoc].summary}</p>
                  <pre style={{ background: '#f8f9fa', padding: '15px', borderRadius: '5px', whiteSpace: 'pre-wrap', fontSize: '13px', lineHeight: 1.6 }}>{modelDocs[selDoc].description}</pre>
                  {modelDocs[selDoc].parameters && (
                    <><h4>Parameters</h4>
                    <table style={{ width: '100%', fontSize: '13px' }}><tbody>
                      {Object.entries(modelDocs[selDoc].parameters).map(([k, v]: [string, any]) => (
                        <tr key={k}><td style={{ padding: '5px', fontWeight: 'bold' }}>{k}</td><td>{v.description}</td><td style={{ color: '#666' }}>Default: {v.default}</td></tr>
                      ))}
                    </tbody></table></>
                  )}
                  {modelDocs[selDoc].references && (<><h4>References</h4><ul>{modelDocs[selDoc].references.map((r: string, i: number) => <li key={i} style={{ fontSize: '13px' }}>{r}</li>)}</ul></>)}
                </>
              ) : <p style={{ color: '#666' }}>Select a model to view documentation</p>}
            </div>
          </div>
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
                <div style={{ padding: '10px', background: '#e3f2fd', borderRadius: '5px', fontSize: '12px', marginTop: '10px' }}>
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
                <div key={u.id} style={{ padding: '8px', borderBottom: '1px solid #eee', cursor: 'pointer' }} onClick={() => loadUniverseDetails(u.id)}>
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
                <p style={{ color: '#666' }}>No custom universes yet</p>
              ) : (
                customUniverses.map(u => (
                  <div key={u.id} style={{ padding: '8px', borderBottom: '1px solid #eee' }}>
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
                        <div key={i} style={{ padding: '8px', background: '#f8f9fa', borderRadius: '5px', cursor: 'pointer' }} onClick={() => loadStockDetails(stock.ticker)}>
                          <div style={{ fontWeight: 'bold' }}>{stock.ticker?.replace('.BK', '')}</div>
                          <div style={{ fontSize: '11px', color: '#666' }}>{stock.name || stock.sector || ''}</div>
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
                      <div key={key} style={{ padding: '10px', background: '#f8f9fa', borderRadius: '5px' }}>
                        <div style={{ fontSize: '11px', color: '#666', marginBottom: '5px' }}>{key.replace(/_/g, ' ').toUpperCase()}</div>
                        <div style={{ fontWeight: 'bold' }}>{value || 'N/A'}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
            
            {/* Edit Custom Universe Modal */}
            {editingUniverse && (
              <div style={{ ...S.card, gridColumn: '1 / -1', background: '#fff', border: '2px solid #4a90d9' }}>
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
              <p style={{ color: '#666', marginBottom: '20px' }}>Test model performance on historical data to identify which models actually work.</p>
              
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
                    <p style={{ color: '#666', fontSize: '12px', margin: 0 }}>Period: {backtestResults.period}</p>
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
                  <div style={{ background: '#f8f9fa', padding: '15px', borderRadius: '8px' }}>
                    <div style={{ fontSize: '11px', color: '#666', marginBottom: '5px' }}>Total Return</div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: backtestResults.performance.total_return_pct >= 0 ? '#28a745' : '#dc3545' }}>
                      {backtestResults.performance.total_return_pct >= 0 ? '+' : ''}{backtestResults.performance.total_return_pct.toFixed(2)}%
                    </div>
                  </div>
                  
                  <div style={{ background: '#f8f9fa', padding: '15px', borderRadius: '8px' }}>
                    <div style={{ fontSize: '11px', color: '#666', marginBottom: '5px' }}>Annualized Return</div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: backtestResults.performance.annualized_return_pct >= 0 ? '#28a745' : '#dc3545' }}>
                      {backtestResults.performance.annualized_return_pct >= 0 ? '+' : ''}{backtestResults.performance.annualized_return_pct.toFixed(2)}%
                    </div>
                  </div>
                  
                  <div style={{ background: '#f8f9fa', padding: '15px', borderRadius: '8px' }}>
                    <div style={{ fontSize: '11px', color: '#666', marginBottom: '5px' }}>Sharpe Ratio</div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: backtestResults.performance.sharpe_ratio >= 1 ? '#28a745' : backtestResults.performance.sharpe_ratio >= 0.5 ? '#ffc107' : '#dc3545' }}>
                      {backtestResults.performance.sharpe_ratio.toFixed(2)}
                    </div>
                  </div>
                  
                  <div style={{ background: '#f8f9fa', padding: '15px', borderRadius: '8px' }}>
                    <div style={{ fontSize: '11px', color: '#666', marginBottom: '5px' }}>Max Drawdown</div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#dc3545' }}>
                      {backtestResults.performance.max_drawdown_pct.toFixed(2)}%
                    </div>
                  </div>
                  
                  <div style={{ background: '#f8f9fa', padding: '15px', borderRadius: '8px' }}>
                    <div style={{ fontSize: '11px', color: '#666', marginBottom: '5px' }}>Final Value</div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
                      ${backtestResults.performance.final_value.toLocaleString()}
                    </div>
                  </div>
                </div>
                
                {/* Trade Statistics */}
                <h4 style={{ marginTop: '30px', marginBottom: '15px' }}>Trade Statistics</h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '15px', marginBottom: '30px' }}>
                  <div>
                    <div style={{ fontSize: '12px', color: '#666' }}>Total Trades</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{backtestResults.trades.total}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: '#666' }}>Win Rate</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: backtestResults.trades.win_rate_pct >= 50 ? '#28a745' : '#dc3545' }}>
                      {backtestResults.trades.win_rate_pct.toFixed(1)}%
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: '#666' }}>Winning Trades</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#28a745' }}>{backtestResults.trades.winning}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: '#666' }}>Losing Trades</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#dc3545' }}>{backtestResults.trades.losing}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: '#666' }}>Avg Win</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#28a745' }}>
                      +{backtestResults.trades.avg_win_pct.toFixed(2)}%
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: '#666' }}>Avg Loss</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#dc3545' }}>
                      {backtestResults.trades.avg_loss_pct.toFixed(2)}%
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: '#666' }}>Profit Factor</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: backtestResults.trades.profit_factor >= 1.5 ? '#28a745' : backtestResults.trades.profit_factor >= 1 ? '#ffc107' : '#dc3545' }}>
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
                        <thead style={{ position: 'sticky', top: 0, background: '#f8f9fa', zIndex: 1 }}>
                          <tr style={{ background: '#f8f9fa' }}>
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
                            <tr key={i} style={{ borderBottom: '1px solid #eee' }}>
                              <td style={{ padding: '8px' }}>{new Date(trade.entry_date).toLocaleDateString()}</td>
                              <td style={{ padding: '8px' }}>{new Date(trade.exit_date).toLocaleDateString()}</td>
                              <td style={{ padding: '8px', fontWeight: 'bold' }}>{trade.ticker.replace('.BK', '')}</td>
                              <td style={{ padding: '8px', textAlign: 'right' }}>${trade.entry_price.toFixed(2)}</td>
                              <td style={{ padding: '8px', textAlign: 'right' }}>${trade.exit_price.toFixed(2)}</td>
                              <td style={{ padding: '8px', textAlign: 'right', color: trade.return_pct >= 0 ? '#28a745' : '#dc3545', fontWeight: 'bold' }}>
                                {trade.return_pct >= 0 ? '+' : ''}{trade.return_pct.toFixed(2)}%
                              </td>
                              <td style={{ padding: '8px', textAlign: 'right', color: trade.pnl >= 0 ? '#28a745' : '#dc3545', fontWeight: 'bold' }}>
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
              <p style={{ color: '#666', marginBottom: '20px' }}>Run multiple models and find stocks with confirmation from multiple signals. Higher confidence = better signals.</p>
              
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
                  <small style={{ color: '#666', fontSize: '11px' }}>How many models must agree</small>
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
                <div style={{ marginTop: '20px', padding: '15px', background: '#f8f9fa', borderRadius: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                    <h4 style={{ marginTop: 0 }}>Results ({signalCombinerResults.total_models_analyzed || 0} models analyzed)</h4>
                    <button style={{ ...S.btn('primary'), fontSize: '12px', padding: '6px 12px' }} onClick={() => downloadSignalCombinerPDF(signalCombinerResults)}>
                      📄 Download PDF
                    </button>
                  </div>
                  
                  {signalCombinerResults.strong_buy_signals && signalCombinerResults.strong_buy_signals.length > 0 && (
                    <div style={{ marginBottom: '20px' }}>
                      <h5 style={{ color: '#28a745', marginBottom: '10px' }}>🟢 Strong Buy Signals ({signalCombinerResults.strong_buy_signals.length})</h5>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '10px' }}>
                        {signalCombinerResults.strong_buy_signals.map((s: any, i: number) => (
                          <div key={i} style={{ background: 'white', padding: '10px', borderRadius: '5px', fontSize: '12px' }}>
                            <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>{s.ticker.replace('.BK', '')}</div>
                            <div style={{ color: '#666' }}>{s.confirmations} confirmations • Score: {s.avg_score}</div>
                            <div style={{ fontSize: '11px', color: '#999', marginTop: '3px' }}>{s.models?.join(', ')}</div>
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
                            <div style={{ color: '#666' }}>{s.confirmations} confirmations • Score: {s.avg_score}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {signalCombinerResults.strong_sell_signals && signalCombinerResults.strong_sell_signals.length > 0 && (
                    <div>
                      <h5 style={{ color: '#dc3545', marginBottom: '10px' }}>🔴 Strong Sell Signals ({signalCombinerResults.strong_sell_signals.length})</h5>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '10px' }}>
                        {signalCombinerResults.strong_sell_signals.map((s: any, i: number) => (
                          <div key={i} style={{ background: 'white', padding: '10px', borderRadius: '5px', fontSize: '12px' }}>
                            <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>{s.ticker.replace('.BK', '')}</div>
                            <div style={{ color: '#666' }}>{s.confirmations} confirmations • Score: {s.avg_score}</div>
                            <div style={{ fontSize: '11px', color: '#999', marginTop: '3px' }}>{s.models?.join(', ')}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {(!signalCombinerResults.strong_buy_signals || signalCombinerResults.strong_buy_signals.length === 0) && 
                   (!signalCombinerResults.moderate_buy_signals || signalCombinerResults.moderate_buy_signals.length === 0) &&
                   (!signalCombinerResults.strong_sell_signals || signalCombinerResults.strong_sell_signals.length === 0) && (
                    <p style={{ color: '#666', fontStyle: 'italic' }}>No signals found with the specified confirmation threshold. Try lowering the minimum confirmation.</p>
                  )}
                </div>
              )}
            </div>
            
            {/* Sector Rotation */}
            <div style={S.card}>
              <h2 style={{ marginTop: 0 }}>🔄 Sector Rotation</h2>
              <p style={{ color: '#666', marginBottom: '20px' }}>Identify which sectors are strongest/weakest for rotation strategies.</p>
              
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
                              <tr key={i} style={{ borderBottom: '1px solid #eee' }}>
                                <td style={{ padding: '8px', fontWeight: 'bold' }}>#{s.rank}</td>
                                <td style={{ padding: '8px', fontWeight: 'bold' }}>{s.sector}</td>
                                <td style={{ padding: '8px', textAlign: 'right' }}>{s.momentum_score.toFixed(2)}</td>
                                <td style={{ padding: '8px', textAlign: 'right', color: s.return_1w >= 0 ? '#28a745' : '#dc3545' }}>
                                  {s.return_1w >= 0 ? '+' : ''}{s.return_1w.toFixed(2)}%
                                </td>
                                <td style={{ padding: '8px', textAlign: 'right', color: s.return_1m >= 0 ? '#28a745' : '#dc3545' }}>
                                  {s.return_1m >= 0 ? '+' : ''}{s.return_1m.toFixed(2)}%
                                </td>
                                <td style={{ padding: '8px', textAlign: 'right', color: s.return_3m >= 0 ? '#28a745' : '#dc3545' }}>
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
              <div style={{ maxHeight: '300px', overflow: 'auto', fontFamily: 'monospace', fontSize: '12px' }}>
                {logs.slice().reverse().map((l, i) => (
                  <div key={i} style={{ padding: '6px', borderLeft: `3px solid ${l.type === 'error' ? '#dc3545' : l.type === 'success' ? '#28a745' : '#17a2b8'}`, background: l.type === 'error' ? '#fff5f5' : l.type === 'success' ? '#f0fff4' : '#f0f9ff', marginBottom: '3px' }}>
                    [{l.time}] {l.message}
                  </div>
                ))}
              </div>
              <button style={{ ...S.btn('secondary'), marginTop: '10px' }} onClick={() => setLogs([])}>Clear</button>
            </div>
            <div style={S.card}>
              <h3 style={{ marginTop: 0 }}>🔧 Troubleshooting</h3>
              <ol><li>Open terminal in <code>backend</code> folder</li><li>Run: <code>pip install -r requirements.txt</code></li><li>Run: <code>uvicorn app.main:app --reload --port 8000</code></li><li>Test: <a href="http://localhost:8000/health" target="_blank">http://localhost:8000/health</a></li></ol>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

// Model Card Component
function ModelCard({ model, result, running, onRun, onPDF }: { model: Model; result?: ModelResult; running: boolean; onRun: () => void; onPDF: (id: string) => void }) {
  return (
    <div style={S.card}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div><h3 style={{ margin: 0 }}>{model.name}</h3><span style={{ fontSize: '11px', padding: '2px 6px', borderRadius: '3px', background: model.category === 'Technical' ? '#cce5ff' : '#e2d5f1' }}>{model.category}</span></div>
        <button style={{ ...S.btn('primary'), opacity: running ? 0.6 : 1 }} onClick={onRun} disabled={running}>{running ? '⏳...' : '▶ Run'}</button>
      </div>
      <p style={{ color: '#666', fontSize: '12px', margin: '10px 0' }}>{model.description}</p>
      {result && (
        <div style={{ borderTop: '1px solid #eee', paddingTop: '10px' }}>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '8px', fontSize: '12px', flexWrap: 'wrap' }}>
            <span style={{ color: '#28a745' }}>✅ {result.buy_signals.length} Buy</span>
            <span style={{ color: '#dc3545' }}>🔻 {result.sell_signals.length} Sell</span>
            <span style={{ color: '#666' }}>{result.stocks_with_data}/{result.total_stocks_analyzed} stocks</span>
            <span style={{ color: '#999', fontSize: '11px', fontStyle: 'italic' }}>(Top signals shown)</span>
          </div>
          {result.buy_signals.slice(0, 4).map((s, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', padding: '3px 0' }}>
              <b>{s.ticker.replace('.BK', '')}</b><span>${s.price_at_signal.toFixed(2)}</span><span style={{ color: '#28a745' }}>{s.score.toFixed(0)}</span>
            </div>
          ))}
          <button style={{ ...S.btn('secondary'), marginTop: '8px', fontSize: '11px' }} onClick={() => onPDF(result.run_id)}>📄 Download PDF</button>
        </div>
      )}
    </div>
  );
}
