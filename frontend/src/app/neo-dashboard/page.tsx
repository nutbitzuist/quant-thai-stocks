'use client';

import React, { useState } from 'react';

// Neo-Brutalist Dashboard Prototype - HQ0.com inspired theme
export default function NeoDashboard() {
  const [activeNav, setActiveNav] = useState('overview');
  const [darkMode, setDarkMode] = useState(false);

  // Sample data for the dashboard
  const portfolioData = {
    totalValue: 2547832.50,
    dailyChange: 32456.78,
    dailyChangePercent: 1.29,
    accounts: 4,
    positions: 12,
  };

  const topPerformers = [
    { symbol: 'PTT', name: 'PTT Public Company', change: 5.42, price: 35.25 },
    { symbol: 'ADVANC', name: 'Advanced Info Service', change: 3.21, price: 248.00 },
    { symbol: 'GULF', name: 'Gulf Energy Development', change: 2.87, price: 52.75 },
    { symbol: 'CPALL', name: 'CP All Public Company', change: 1.95, price: 62.50 },
  ];

  const recentTrades = [
    { time: '14:32', symbol: 'PTT', action: 'BUY', qty: 1000, price: 35.00, status: 'Filled' },
    { time: '13:45', symbol: 'KBANK', action: 'SELL', qty: 500, price: 142.50, status: 'Filled' },
    { time: '11:20', symbol: 'AOT', action: 'BUY', qty: 200, price: 67.25, status: 'Partial' },
    { time: '10:15', symbol: 'BDMS', action: 'BUY', qty: 800, price: 28.50, status: 'Filled' },
  ];

  const signals = [
    { model: 'Momentum Alpha', symbol: 'SCC', signal: 'BUY', confidence: 87 },
    { model: 'Mean Reversion', symbol: 'TRUE', signal: 'SELL', confidence: 72 },
    { model: 'ML Predictor', symbol: 'DELTA', signal: 'BUY', confidence: 91 },
  ];

  const bgColor = darkMode ? '#1a1a1a' : '#f5f5f0';
  const cardBg = darkMode ? '#2a2a2a' : '#ffffff';
  const textColor = darkMode ? '#ffffff' : '#000000';
  const borderColor = darkMode ? '#444444' : '#000000';

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: bgColor,
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
      color: textColor,
      transition: 'all 0.3s ease',
    }}>
      {/* Top Navigation */}
      <header style={{
        backgroundColor: cardBg,
        borderBottom: `3px solid ${borderColor}`,
        padding: '16px 24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '42px',
            height: '42px',
            backgroundColor: '#f2711c',
            border: `3px solid ${borderColor}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 'bold',
            fontSize: '18px',
            color: '#fff',
            boxShadow: `4px 4px 0 ${borderColor}`,
          }}>
            AS
          </div>
          <span style={{ fontWeight: 'bold', fontSize: '20px' }}>AlgoStack</span>
          <span style={{
            backgroundColor: '#f2711c',
            color: '#fff',
            padding: '4px 10px',
            fontSize: '11px',
            fontWeight: 'bold',
            border: `2px solid ${borderColor}`,
            marginLeft: '8px',
            transform: 'rotate(-2deg)',
            display: 'inline-block',
          }}>PRO</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button
            onClick={() => setDarkMode(!darkMode)}
            style={{
              padding: '10px 16px',
              backgroundColor: darkMode ? '#f2711c' : cardBg,
              border: `2px solid ${borderColor}`,
              cursor: 'pointer',
              fontWeight: 'bold',
              fontSize: '14px',
              color: darkMode ? '#fff' : textColor,
              boxShadow: `3px 3px 0 ${borderColor}`,
              transition: 'all 0.1s ease',
            }}
            onMouseDown={(e) => {
              e.currentTarget.style.transform = 'translate(2px, 2px)';
              e.currentTarget.style.boxShadow = `1px 1px 0 ${borderColor}`;
            }}
            onMouseUp={(e) => {
              e.currentTarget.style.transform = 'translate(0, 0)';
              e.currentTarget.style.boxShadow = `3px 3px 0 ${borderColor}`;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translate(0, 0)';
              e.currentTarget.style.boxShadow = `3px 3px 0 ${borderColor}`;
            }}
          >
            {darkMode ? '☀️ LIGHT' : '🌙 DARK'}
          </button>
          <div style={{
            width: '40px',
            height: '40px',
            backgroundColor: '#e0e0e0',
            border: `2px solid ${borderColor}`,
            borderRadius: '0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 'bold',
          }}>
            NT
          </div>
        </div>
      </header>

      <div style={{ display: 'flex' }}>
        {/* Sidebar Navigation */}
        <aside style={{
          width: '220px',
          backgroundColor: cardBg,
          borderRight: `3px solid ${borderColor}`,
          minHeight: 'calc(100vh - 75px)',
          padding: '20px 12px',
        }}>
          {[
            { id: 'overview', label: '📊 Overview', active: true },
            { id: 'portfolio', label: '💼 Portfolio' },
            { id: 'models', label: '🤖 Models' },
            { id: 'signals', label: '📡 Signals' },
            { id: 'history', label: '📜 History' },
            { id: 'analytics', label: '📈 Analytics' },
            { id: 'settings', label: '⚙️ Settings' },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveNav(item.id)}
              style={{
                width: '100%',
                padding: '14px 16px',
                marginBottom: '8px',
                backgroundColor: activeNav === item.id ? '#f2711c' : 'transparent',
                color: activeNav === item.id ? '#fff' : textColor,
                border: `2px solid ${activeNav === item.id ? borderColor : 'transparent'}`,
                textAlign: 'left',
                fontWeight: 'bold',
                fontSize: '14px',
                cursor: 'pointer',
                boxShadow: activeNav === item.id ? `3px 3px 0 ${borderColor}` : 'none',
                transition: 'all 0.1s ease',
              }}
            >
              {item.label}
            </button>
          ))}
        </aside>

        {/* Main Content */}
        <main style={{ flex: 1, padding: '24px' }}>
          {/* Page Title */}
          <div style={{ marginBottom: '24px' }}>
            <h1 style={{
              fontSize: '32px',
              fontWeight: 'bold',
              margin: 0,
              display: 'inline-block',
              borderBottom: `4px solid #f2711c`,
              paddingBottom: '4px',
            }}>
              Dashboard Overview
            </h1>
            <p style={{ color: darkMode ? '#888' : '#666', marginTop: '8px' }}>
              December 25, 2024 • Market Open
            </p>
          </div>

          {/* Stats Cards Row */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '20px',
            marginBottom: '24px',
          }}>
            {/* Total Portfolio Value */}
            <div style={{
              backgroundColor: cardBg,
              border: `3px solid ${borderColor}`,
              padding: '20px',
              boxShadow: `6px 6px 0 ${borderColor}`,
            }}>
              <div style={{ fontSize: '12px', fontWeight: 'bold', color: darkMode ? '#888' : '#666', marginBottom: '8px' }}>
                TOTAL PORTFOLIO
              </div>
              <div style={{ fontSize: '28px', fontWeight: 'bold' }}>
                ฿{portfolioData.totalValue.toLocaleString()}
              </div>
              <div style={{
                display: 'inline-block',
                marginTop: '8px',
                padding: '4px 8px',
                backgroundColor: '#22c55e',
                color: '#fff',
                fontWeight: 'bold',
                fontSize: '12px',
                border: `2px solid ${borderColor}`,
              }}>
                ↑ +{portfolioData.dailyChangePercent}%
              </div>
            </div>

            {/* Daily P&L */}
            <div style={{
              backgroundColor: cardBg,
              border: `3px solid ${borderColor}`,
              padding: '20px',
              boxShadow: `6px 6px 0 #22c55e`,
            }}>
              <div style={{ fontSize: '12px', fontWeight: 'bold', color: darkMode ? '#888' : '#666', marginBottom: '8px' }}>
                TODAY'S P&L
              </div>
              <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#22c55e' }}>
                +฿{portfolioData.dailyChange.toLocaleString()}
              </div>
              <div style={{ color: darkMode ? '#888' : '#666', fontSize: '13px', marginTop: '8px' }}>
                Realized: ฿12,450
              </div>
            </div>

            {/* Active Positions */}
            <div style={{
              backgroundColor: cardBg,
              border: `3px solid ${borderColor}`,
              padding: '20px',
              boxShadow: `6px 6px 0 #f2711c`,
            }}>
              <div style={{ fontSize: '12px', fontWeight: 'bold', color: darkMode ? '#888' : '#666', marginBottom: '8px' }}>
                ACTIVE POSITIONS
              </div>
              <div style={{ fontSize: '28px', fontWeight: 'bold' }}>
                {portfolioData.positions}
              </div>
              <div style={{ color: darkMode ? '#888' : '#666', fontSize: '13px', marginTop: '8px' }}>
                Across {portfolioData.accounts} accounts
              </div>
            </div>

            {/* Win Rate */}
            <div style={{
              backgroundColor: '#f2711c',
              border: `3px solid ${borderColor}`,
              padding: '20px',
              boxShadow: `6px 6px 0 ${borderColor}`,
              color: '#fff',
            }}>
              <div style={{ fontSize: '12px', fontWeight: 'bold', opacity: 0.9, marginBottom: '8px' }}>
                WIN RATE (30D)
              </div>
              <div style={{ fontSize: '28px', fontWeight: 'bold' }}>
                68.5%
              </div>
              <div style={{ opacity: 0.9, fontSize: '13px', marginTop: '8px' }}>
                23W / 8L • 4 Pending
              </div>
            </div>
          </div>

          {/* Two Column Layout */}
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
            {/* Left Column */}
            <div>
              {/* Recent Trades Table */}
              <div style={{
                backgroundColor: cardBg,
                border: `3px solid ${borderColor}`,
                boxShadow: `6px 6px 0 ${borderColor}`,
                marginBottom: '24px',
              }}>
                <div style={{
                  borderBottom: `3px solid ${borderColor}`,
                  padding: '16px 20px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}>
                  <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>
                    Recent Trades
                  </h2>
                  <button style={{
                    padding: '8px 14px',
                    backgroundColor: 'transparent',
                    border: `2px solid ${borderColor}`,
                    fontWeight: 'bold',
                    fontSize: '12px',
                    cursor: 'pointer',
                    color: textColor,
                  }}>
                    VIEW ALL →
                  </button>
                </div>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ backgroundColor: darkMode ? '#333' : '#f0f0f0' }}>
                      {['TIME', 'SYMBOL', 'ACTION', 'QTY', 'PRICE', 'STATUS'].map((header) => (
                        <th key={header} style={{
                          padding: '12px 16px',
                          textAlign: 'left',
                          fontSize: '11px',
                          fontWeight: 'bold',
                          borderBottom: `2px solid ${borderColor}`,
                        }}>
                          {header}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {recentTrades.map((trade, idx) => (
                      <tr key={idx} style={{
                        backgroundColor: idx % 2 === 0 ? 'transparent' : (darkMode ? '#333' : '#fafafa'),
                      }}>
                        <td style={{ padding: '14px 16px', fontSize: '14px' }}>{trade.time}</td>
                        <td style={{ padding: '14px 16px', fontWeight: 'bold', fontSize: '14px' }}>{trade.symbol}</td>
                        <td style={{ padding: '14px 16px' }}>
                          <span style={{
                            padding: '4px 10px',
                            backgroundColor: trade.action === 'BUY' ? '#22c55e' : '#ef4444',
                            color: '#fff',
                            fontWeight: 'bold',
                            fontSize: '11px',
                            border: `2px solid ${borderColor}`,
                          }}>
                            {trade.action}
                          </span>
                        </td>
                        <td style={{ padding: '14px 16px', fontSize: '14px' }}>{trade.qty.toLocaleString()}</td>
                        <td style={{ padding: '14px 16px', fontSize: '14px' }}>฿{trade.price.toFixed(2)}</td>
                        <td style={{ padding: '14px 16px' }}>
                          <span style={{
                            padding: '4px 10px',
                            backgroundColor: trade.status === 'Filled' ? (darkMode ? '#333' : '#f0f0f0') : '#fef3c7',
                            fontWeight: 'bold',
                            fontSize: '11px',
                            border: `2px solid ${borderColor}`,
                            color: textColor,
                          }}>
                            {trade.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Chart Placeholder */}
              <div style={{
                backgroundColor: cardBg,
                border: `3px solid ${borderColor}`,
                boxShadow: `6px 6px 0 ${borderColor}`,
                padding: '20px',
              }}>
                <h2 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: 'bold' }}>
                  Portfolio Performance
                </h2>
                <div style={{
                  height: '200px',
                  backgroundColor: darkMode ? '#333' : '#f5f5f5',
                  border: `2px dashed ${borderColor}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: darkMode ? '#888' : '#666',
                }}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '48px', marginBottom: '8px' }}>📈</div>
                    <div style={{ fontWeight: 'bold' }}>Portfolio Chart Area</div>
                    <div style={{ fontSize: '13px' }}>Interactive chart will be rendered here</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column */}
            <div>
              {/* Top Performers */}
              <div style={{
                backgroundColor: cardBg,
                border: `3px solid ${borderColor}`,
                boxShadow: `6px 6px 0 ${borderColor}`,
                marginBottom: '24px',
              }}>
                <div style={{
                  borderBottom: `3px solid ${borderColor}`,
                  padding: '16px 20px',
                }}>
                  <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>
                    🔥 Top Performers
                  </h2>
                </div>
                <div style={{ padding: '12px' }}>
                  {topPerformers.map((stock, idx) => (
                    <div key={idx} style={{
                      padding: '12px',
                      borderBottom: idx < topPerformers.length - 1 ? `2px solid ${darkMode ? '#444' : '#eee'}` : 'none',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}>
                      <div>
                        <div style={{ fontWeight: 'bold', fontSize: '15px' }}>{stock.symbol}</div>
                        <div style={{ fontSize: '12px', color: darkMode ? '#888' : '#666' }}>
                          {stock.name.substring(0, 20)}...
                        </div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontWeight: 'bold' }}>฿{stock.price.toFixed(2)}</div>
                        <div style={{
                          color: '#22c55e',
                          fontWeight: 'bold',
                          fontSize: '13px',
                        }}>
                          +{stock.change}%
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Active Signals */}
              <div style={{
                backgroundColor: cardBg,
                border: `3px solid ${borderColor}`,
                boxShadow: `6px 6px 0 #f2711c`,
              }}>
                <div style={{
                  borderBottom: `3px solid ${borderColor}`,
                  padding: '16px 20px',
                  backgroundColor: '#f2711c',
                  color: '#fff',
                }}>
                  <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>
                    ⚡ Active Signals
                  </h2>
                </div>
                <div style={{ padding: '12px' }}>
                  {signals.map((sig, idx) => (
                    <div key={idx} style={{
                      padding: '14px',
                      border: `2px solid ${borderColor}`,
                      marginBottom: '10px',
                      backgroundColor: darkMode ? '#333' : '#fafafa',
                    }}>
                      <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: '8px',
                      }}>
                        <span style={{ fontWeight: 'bold', fontSize: '16px' }}>{sig.symbol}</span>
                        <span style={{
                          padding: '4px 10px',
                          backgroundColor: sig.signal === 'BUY' ? '#22c55e' : '#ef4444',
                          color: '#fff',
                          fontWeight: 'bold',
                          fontSize: '11px',
                          border: `2px solid ${borderColor}`,
                        }}>
                          {sig.signal}
                        </span>
                      </div>
                      <div style={{
                        fontSize: '12px',
                        color: darkMode ? '#888' : '#666',
                        marginBottom: '8px',
                      }}>
                        {sig.model}
                      </div>
                      <div style={{
                        height: '8px',
                        backgroundColor: darkMode ? '#444' : '#e0e0e0',
                        border: `1px solid ${borderColor}`,
                      }}>
                        <div style={{
                          height: '100%',
                          width: `${sig.confidence}%`,
                          backgroundColor: '#f2711c',
                        }} />
                      </div>
                      <div style={{
                        fontSize: '11px',
                        fontWeight: 'bold',
                        marginTop: '4px',
                        color: darkMode ? '#888' : '#666',
                      }}>
                        {sig.confidence}% confidence
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions Bar */}
          <div style={{
            marginTop: '24px',
            display: 'flex',
            gap: '12px',
          }}>
            {[
              { label: '+ New Trade', primary: true },
              { label: '🔄 Refresh Data' },
              { label: '📥 Export Report' },
              { label: '⚙️ Configure Alerts' },
            ].map((btn, idx) => (
              <button
                key={idx}
                style={{
                  padding: '14px 24px',
                  backgroundColor: btn.primary ? '#f2711c' : cardBg,
                  color: btn.primary ? '#fff' : textColor,
                  border: `3px solid ${borderColor}`,
                  fontWeight: 'bold',
                  fontSize: '14px',
                  cursor: 'pointer',
                  boxShadow: `4px 4px 0 ${borderColor}`,
                  transition: 'all 0.1s ease',
                }}
                onMouseDown={(e) => {
                  e.currentTarget.style.transform = 'translate(3px, 3px)';
                  e.currentTarget.style.boxShadow = `1px 1px 0 ${borderColor}`;
                }}
                onMouseUp={(e) => {
                  e.currentTarget.style.transform = 'translate(0, 0)';
                  e.currentTarget.style.boxShadow = `4px 4px 0 ${borderColor}`;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translate(0, 0)';
                  e.currentTarget.style.boxShadow = `4px 4px 0 ${borderColor}`;
                }}
              >
                {btn.label}
              </button>
            ))}
          </div>
        </main>
      </div>

      {/* Footer Badge */}
      <div style={{
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        backgroundColor: '#f2711c',
        color: '#fff',
        padding: '10px 16px',
        fontWeight: 'bold',
        fontSize: '12px',
        border: `3px solid ${borderColor}`,
        boxShadow: `4px 4px 0 ${borderColor}`,
        transform: 'rotate(-3deg)',
      }}>
        ⚡ NEO-BRUTALIST PROTOTYPE
      </div>
    </div>
  );
}
