'use client';

import { useState } from 'react';
import Link from 'next/link';

// All models from the backend - Technical (11), Fundamental (12), Quantitative (4)
const TECHNICAL_MODELS = [
    { name: 'RSI Reversal', desc: 'Buy RSI < 30, Sell RSI > 70', icon: '📊', best: 'Mean reversion' },
    { name: 'MACD Crossover', desc: 'Bullish/bearish crossover signals', icon: '⚡', best: 'Trend following' },
    { name: 'Minervini Trend', desc: 'Stage 2 uptrend template', icon: '🎯', best: 'Growth stocks' },
    { name: 'Darvas Box', desc: 'Breakout from consolidation boxes', icon: '📦', best: 'Breakout trading' },
    { name: 'Turtle Trading', desc: '55-day high breakout system', icon: '🐢', best: 'Trend following' },
    { name: 'Elder Triple Screen', desc: 'Multi-timeframe + Force Index', icon: '🖥️', best: 'Pullback entries' },
    { name: 'ADX Trend', desc: 'Directional movement strength', icon: '📈', best: 'Strong trends' },
    { name: 'Bollinger Squeeze', desc: 'Volatility contraction breakouts', icon: '🎰', best: 'Volatility plays' },
    { name: 'Dual EMA', desc: 'Fast/slow EMA crossovers', icon: '〰️', best: 'Momentum' },
    { name: 'Keltner Channel', desc: 'ATR-based trend channels', icon: '📉', best: 'Channel trading' },
    { name: 'Volume Profile', desc: 'Volume-weighted price analysis', icon: '📊', best: 'Support/resistance' },
];

const FUNDAMENTAL_MODELS = [
    { name: 'CANSLIM', desc: "William O'Neil's 7 criteria", icon: '📈', best: 'Growth investing' },
    { name: 'Value Composite', desc: 'P/E, P/B, P/S, Dividend yield', icon: '💎', best: 'Value investing' },
    { name: 'Quality Score', desc: 'ROE, ROA, margins, debt analysis', icon: '⭐', best: 'Quality focus' },
    { name: 'Piotroski F-Score', desc: '9-point financial strength', icon: '🏆', best: 'Deep value' },
    { name: 'Magic Formula', desc: 'Greenblatt earnings yield + ROIC', icon: '✨', best: 'Value + Quality' },
    { name: 'Altman Z-Score', desc: 'Bankruptcy prediction model', icon: '🛡️', best: 'Risk avoidance' },
    { name: 'Dividend Aristocrats', desc: '25+ years dividend growth', icon: '👑', best: 'Income investing' },
    { name: 'Earnings Momentum', desc: 'EPS acceleration & beats', icon: '🚀', best: 'Growth momentum' },
    { name: 'EV/EBITDA', desc: 'Enterprise value analysis', icon: '🏢', best: 'M&A targets' },
    { name: 'FCF Yield', desc: 'Free cash flow valuation', icon: '💰', best: 'Cash generators' },
    { name: 'GARP', desc: 'Growth at reasonable price', icon: '⚖️', best: 'Balanced growth' },
    { name: 'Momentum Value', desc: 'Combines price & value factors', icon: '🔥', best: 'Factor investing' },
];

const QUANTITATIVE_MODELS = [
    { name: 'Factor Momentum', desc: 'Multi-factor rotation strategy', icon: '🎲', best: 'Smart beta' },
    { name: 'Mean Reversion', desc: 'Statistical reversion to mean', icon: '↩️', best: 'Swing trading' },
    { name: 'Pairs Trading', desc: 'Correlated pairs divergence', icon: '👥', best: 'Market neutral' },
    { name: 'Volatility Breakout', desc: 'Range expansion signals', icon: '💥', best: 'Momentum bursts' },
];

const FEATURES = [
    { title: 'Real-Time Screening', desc: 'Scan S&P 500 and SET100 stocks instantly with 27+ institutional models', icon: '🔍' },
    { title: 'AI-Powered Analysis', desc: 'Comprehensive buy/sell signals with confidence scores and reasoning', icon: '🤖' },
    { title: 'Advanced Backtesting', desc: 'Test any strategy against years of historical data', icon: '📈' },
    { title: 'Custom Universes', desc: 'Create and manage your own watchlists and screening universes', icon: '🌐' },
    { title: 'PDF Reports', desc: 'Generate institutional-quality analysis reports on demand', icon: '📄' },
    { title: 'Multi-Market', desc: 'US (S&P 500) and Thai (SET100) market coverage', icon: '🌏' },
];

const TESTIMONIALS = [
    { name: 'Michael T.', role: 'Portfolio Manager', quote: 'Finally, institutional-grade screening without the $50k terminal cost.', avatar: '👨‍💼' },
    { name: 'Sarah K.', role: 'Independent Trader', quote: 'The Minervini and CANSLIM models alone are worth 10x the subscription.', avatar: '👩‍💻' },
    { name: 'David L.', role: 'Hedge Fund Analyst', quote: 'I use this to validate my manual analysis. Saves me hours every week.', avatar: '👨‍🔬' },
];

export default function LandingPage() {
    const totalModels = TECHNICAL_MODELS.length + FUNDAMENTAL_MODELS.length + QUANTITATIVE_MODELS.length;
    const [isAnnual, setIsAnnual] = useState(true); // Default to annual for better conversion

    return (
        <div style={{ paddingTop: '80px' }}>
            {/* Hero Section - High Conversion */}
            <section style={{
                padding: '5rem 2rem 6rem',
                textAlign: 'center',
                background: 'linear-gradient(180deg, var(--foreground) 0%, #1a1a1a 100%)',
                color: 'var(--background)',
            }}>
                <div style={{ maxWidth: '900px', margin: '0 auto' }}>
                    {/* Urgency Badge */}
                    <div style={{
                        display: 'inline-block',
                        padding: '0.5rem 1.25rem',
                        background: 'var(--primary)',
                        border: '2px solid var(--background)',
                        boxShadow: '3px 3px 0 var(--background)',
                        marginBottom: '2rem',
                        fontSize: '0.875rem',
                        fontWeight: '700',
                        color: 'var(--primary-foreground)',
                        animation: 'pulse 2s infinite',
                    }}>
                        🔥 LAUNCH OFFER: Get 2 Months FREE with Annual Plans
                    </div>

                    {/* Main Headline */}
                    <h1 style={{
                        fontSize: 'clamp(2.5rem, 8vw, 4rem)',
                        fontWeight: '900',
                        lineHeight: '1.1',
                        letterSpacing: '-0.03em',
                        marginBottom: '1.5rem',
                    }}>
                        Stop Losing Money to
                        <br />
                        <span style={{ color: 'var(--primary)' }}>Random Stock Picks</span>
                    </h1>

                    {/* Subheadline - Pain & Solution */}
                    <p style={{
                        fontSize: '1.35rem',
                        color: 'rgba(255,255,255,0.85)',
                        maxWidth: '700px',
                        margin: '0 auto 1.5rem',
                        lineHeight: '1.6',
                    }}>
                        Screen stocks like hedge funds using <strong>{totalModels} institutional-grade models</strong> — CANSLIM,
                        Minervini, Piotroski, and more. The same strategies that manage billions.
                    </p>

                    {/* Value Proposition */}
                    <div style={{
                        display: 'flex',
                        justifyContent: 'center',
                        gap: '2rem',
                        flexWrap: 'wrap',
                        marginBottom: '2.5rem',
                        fontSize: '1rem',
                    }}>
                        <span>✓ {totalModels} Proven Models</span>
                        <span>✓ US & Thai Markets</span>
                        <span>✓ Real-Time Signals</span>
                        <span>✓ Backtesting Included</span>
                    </div>

                    {/* CTA Buttons */}
                    <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
                        <Link href="/sign-up" style={{
                            textDecoration: 'none',
                            padding: '1.125rem 2.5rem',
                            background: 'var(--primary)',
                            color: 'var(--primary-foreground)',
                            border: '3px solid var(--background)',
                            boxShadow: '5px 5px 0 var(--background)',
                            fontWeight: '800',
                            fontSize: '1.15rem',
                            cursor: 'pointer',
                            transition: 'transform 0.1s ease, box-shadow 0.1s ease',
                        }}>
                            Start Your Trial Now →
                        </Link>
                        <Link href="#pricing" style={{
                            textDecoration: 'none',
                            padding: '1.125rem 2.5rem',
                            background: 'transparent',
                            color: 'var(--background)',
                            border: '3px solid var(--background)',
                            boxShadow: '5px 5px 0 rgba(255,255,255,0.2)',
                            fontWeight: '700',
                            fontSize: '1.15rem',
                            cursor: 'pointer',
                        }}>
                            See Pricing
                        </Link>
                    </div>

                    {/* Trust Signals */}
                    <p style={{
                        fontSize: '0.875rem',
                        color: 'rgba(255,255,255,0.6)',
                    }}>
                        ⚡ 7-day money-back guarantee &nbsp;&nbsp; 🔒 Cancel anytime &nbsp;&nbsp; 💳 Secure payments
                    </p>
                </div>
            </section>

            {/* Social Proof */}
            <section style={{
                padding: '3rem 2rem',
                background: 'var(--muted)',
                borderBottom: '3px solid var(--border)',
            }}>
                <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                        gap: '1.5rem',
                    }}>
                        {TESTIMONIALS.map((t, i) => (
                            <div key={i} style={{
                                padding: '1.5rem',
                                background: 'var(--card)',
                                border: '3px solid var(--border)',
                                boxShadow: '4px 4px 0 var(--border)',
                            }}>
                                <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{t.avatar}</div>
                                <p style={{
                                    fontStyle: 'italic',
                                    marginBottom: '1rem',
                                    color: 'var(--foreground)',
                                    fontSize: '0.95rem',
                                    lineHeight: '1.5',
                                }}>
                                    "{t.quote}"
                                </p>
                                <div style={{ fontWeight: '700', fontSize: '0.9rem' }}>{t.name}</div>
                                <div style={{ fontSize: '0.8rem', color: 'var(--muted-foreground)' }}>{t.role}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section id="features" style={{
                padding: '5rem 2rem',
                background: 'var(--background)',
            }}>
                <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
                    <h2 style={{
                        textAlign: 'center',
                        fontSize: '2.5rem',
                        fontWeight: '900',
                        marginBottom: '1rem',
                        letterSpacing: '-0.02em',
                    }}>
                        Everything You Need to Outperform
                    </h2>
                    <p style={{
                        textAlign: 'center',
                        color: 'var(--muted-foreground)',
                        marginBottom: '3rem',
                        fontSize: '1.1rem',
                    }}>
                        Professional tools that used to cost $25,000/year — now accessible to you
                    </p>

                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
                        gap: '1.5rem',
                    }}>
                        {FEATURES.map((feature, i) => (
                            <div key={i} style={{
                                padding: '1.5rem',
                                background: 'var(--card)',
                                border: '3px solid var(--border)',
                                boxShadow: '4px 4px 0 var(--border)',
                            }}>
                                <div style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>{feature.icon}</div>
                                <h3 style={{
                                    fontSize: '1.25rem',
                                    fontWeight: '800',
                                    marginBottom: '0.5rem',
                                }}>
                                    {feature.title}
                                </h3>
                                <p style={{ color: 'var(--muted-foreground)', lineHeight: '1.5' }}>
                                    {feature.desc}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Models Section - All Models */}
            <section id="models" style={{
                padding: '5rem 2rem',
                background: 'var(--muted)',
            }}>
                <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
                    <h2 style={{
                        textAlign: 'center',
                        fontSize: '2.5rem',
                        fontWeight: '900',
                        marginBottom: '1rem',
                    }}>
                        {totalModels} Battle-Tested Models
                    </h2>
                    <p style={{
                        textAlign: 'center',
                        color: 'var(--muted-foreground)',
                        marginBottom: '3rem',
                        fontSize: '1.1rem',
                    }}>
                        From legendary investors to cutting-edge quant strategies
                    </p>

                    {/* Technical Models */}
                    <h3 style={{
                        fontSize: '1.5rem',
                        fontWeight: '800',
                        marginBottom: '1rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                    }}>
                        <span style={{
                            display: 'inline-block',
                            width: '12px',
                            height: '12px',
                            background: 'var(--primary)',
                            border: '2px solid var(--border)'
                        }}></span>
                        Technical Models ({TECHNICAL_MODELS.length})
                    </h3>
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
                        gap: '1rem',
                        marginBottom: '2rem',
                    }}>
                        {TECHNICAL_MODELS.map((model, i) => (
                            <div key={i} style={{
                                padding: '1rem',
                                background: 'var(--card)',
                                border: '3px solid var(--border)',
                                boxShadow: '3px 3px 0 var(--border)',
                                display: 'flex',
                                alignItems: 'flex-start',
                                gap: '0.75rem',
                            }}>
                                <div style={{
                                    width: '40px',
                                    height: '40px',
                                    background: 'var(--primary)',
                                    border: '2px solid var(--border)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    fontSize: '1.25rem',
                                    flexShrink: 0,
                                }}>
                                    {model.icon}
                                </div>
                                <div>
                                    <h4 style={{ fontSize: '0.95rem', fontWeight: '700', marginBottom: '0.25rem' }}>{model.name}</h4>
                                    <p style={{ fontSize: '0.8rem', color: 'var(--muted-foreground)', marginBottom: '0.25rem' }}>{model.desc}</p>
                                    <span style={{ fontSize: '0.7rem', color: 'var(--primary)', fontWeight: '600' }}>{model.best}</span>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Fundamental Models */}
                    <h3 style={{
                        fontSize: '1.5rem',
                        fontWeight: '800',
                        marginBottom: '1rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                    }}>
                        <span style={{
                            display: 'inline-block',
                            width: '12px',
                            height: '12px',
                            background: 'var(--success)',
                            border: '2px solid var(--border)'
                        }}></span>
                        Fundamental Models ({FUNDAMENTAL_MODELS.length})
                    </h3>
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
                        gap: '1rem',
                        marginBottom: '2rem',
                    }}>
                        {FUNDAMENTAL_MODELS.map((model, i) => (
                            <div key={i} style={{
                                padding: '1rem',
                                background: 'var(--card)',
                                border: '3px solid var(--border)',
                                boxShadow: '3px 3px 0 var(--border)',
                                display: 'flex',
                                alignItems: 'flex-start',
                                gap: '0.75rem',
                            }}>
                                <div style={{
                                    width: '40px',
                                    height: '40px',
                                    background: 'var(--success)',
                                    border: '2px solid var(--border)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    fontSize: '1.25rem',
                                    flexShrink: 0,
                                }}>
                                    {model.icon}
                                </div>
                                <div>
                                    <h4 style={{ fontSize: '0.95rem', fontWeight: '700', marginBottom: '0.25rem' }}>{model.name}</h4>
                                    <p style={{ fontSize: '0.8rem', color: 'var(--muted-foreground)', marginBottom: '0.25rem' }}>{model.desc}</p>
                                    <span style={{ fontSize: '0.7rem', color: 'var(--success)', fontWeight: '600' }}>{model.best}</span>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Quantitative Models */}
                    <h3 style={{
                        fontSize: '1.5rem',
                        fontWeight: '800',
                        marginBottom: '1rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                    }}>
                        <span style={{
                            display: 'inline-block',
                            width: '12px',
                            height: '12px',
                            background: '#8b5cf6',
                            border: '2px solid var(--border)'
                        }}></span>
                        Quantitative Models ({QUANTITATIVE_MODELS.length})
                    </h3>
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
                        gap: '1rem',
                    }}>
                        {QUANTITATIVE_MODELS.map((model, i) => (
                            <div key={i} style={{
                                padding: '1rem',
                                background: 'var(--card)',
                                border: '3px solid var(--border)',
                                boxShadow: '3px 3px 0 var(--border)',
                                display: 'flex',
                                alignItems: 'flex-start',
                                gap: '0.75rem',
                            }}>
                                <div style={{
                                    width: '40px',
                                    height: '40px',
                                    background: '#8b5cf6',
                                    border: '2px solid var(--border)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    fontSize: '1.25rem',
                                    flexShrink: 0,
                                }}>
                                    {model.icon}
                                </div>
                                <div>
                                    <h4 style={{ fontSize: '0.95rem', fontWeight: '700', marginBottom: '0.25rem' }}>{model.name}</h4>
                                    <p style={{ fontSize: '0.8rem', color: 'var(--muted-foreground)', marginBottom: '0.25rem' }}>{model.desc}</p>
                                    <span style={{ fontSize: '0.7rem', color: '#8b5cf6', fontWeight: '600' }}>{model.best}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Pricing Section */}
            <section id="pricing" style={{
                padding: '5rem 2rem',
                background: 'var(--background)',
            }}>
                <div style={{ maxWidth: '900px', margin: '0 auto' }}>
                    <h2 style={{
                        textAlign: 'center',
                        fontSize: '2.5rem',
                        fontWeight: '900',
                        marginBottom: '1rem',
                    }}>
                        Invest in Your Edge
                    </h2>
                    <p style={{
                        textAlign: 'center',
                        color: 'var(--muted-foreground)',
                        marginBottom: '2rem',
                        fontSize: '1.1rem',
                    }}>
                        One winning trade pays for a year of QuantStack
                    </p>

                    {/* Billing Toggle */}
                    <div style={{
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                        gap: '1rem',
                        marginBottom: '3rem',
                    }}>
                        <span style={{
                            fontWeight: isAnnual ? '500' : '700',
                            color: isAnnual ? 'var(--muted-foreground)' : 'var(--foreground)',
                            fontSize: '1rem',
                        }}>
                            Monthly
                        </span>
                        <button
                            onClick={() => setIsAnnual(!isAnnual)}
                            style={{
                                width: '60px',
                                height: '32px',
                                borderRadius: '0',
                                border: '3px solid var(--border)',
                                background: isAnnual ? 'var(--primary)' : 'var(--muted)',
                                cursor: 'pointer',
                                position: 'relative',
                                boxShadow: '3px 3px 0 var(--border)',
                                transition: 'background 0.2s ease',
                            }}
                        >
                            <div style={{
                                width: '20px',
                                height: '20px',
                                background: 'var(--foreground)',
                                border: '2px solid var(--border)',
                                position: 'absolute',
                                top: '3px',
                                left: isAnnual ? '32px' : '4px',
                                transition: 'left 0.2s ease',
                            }} />
                        </button>
                        <span style={{
                            fontWeight: isAnnual ? '700' : '500',
                            color: isAnnual ? 'var(--foreground)' : 'var(--muted-foreground)',
                            fontSize: '1rem',
                        }}>
                            Yearly
                        </span>
                        {isAnnual && (
                            <span style={{
                                background: 'var(--success)',
                                color: 'white',
                                padding: '0.25rem 0.75rem',
                                fontSize: '0.75rem',
                                fontWeight: '700',
                                border: '2px solid var(--border)',
                            }}>
                                2 MONTHS FREE
                            </span>
                        )}
                    </div>

                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
                        gap: '2rem',
                    }}>
                        {/* Pro Plan */}
                        <div style={{
                            padding: '2.5rem',
                            background: 'var(--card)',
                            border: '3px solid var(--border)',
                            boxShadow: '5px 5px 0 var(--border)',
                        }}>
                            <h3 style={{ fontSize: '1.5rem', fontWeight: '800', marginBottom: '0.5rem' }}>Pro</h3>
                            <p style={{ color: 'var(--muted-foreground)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
                                Perfect for active traders
                            </p>
                            <div style={{ marginBottom: '0.5rem' }}>
                                <span style={{ fontSize: '3.5rem', fontWeight: '900' }}>
                                    ${isAnnual ? '41' : '49'}
                                </span>
                                <span style={{ fontSize: '1.1rem', fontWeight: '500', color: 'var(--muted-foreground)' }}>/mo</span>
                            </div>
                            {isAnnual && (
                                <p style={{ fontSize: '0.85rem', color: 'var(--muted-foreground)', marginBottom: '1rem' }}>
                                    <s>$588</s> → <strong>$490/year</strong> (Save $98)
                                </p>
                            )}
                            <p style={{
                                color: 'var(--primary)',
                                fontWeight: '700',
                                marginBottom: '1.5rem',
                                fontSize: '1rem',
                                padding: '0.5rem',
                                background: 'rgba(242, 113, 28, 0.1)',
                                border: '2px solid var(--primary)',
                            }}>
                                📊 150 stock scans/month
                            </p>
                            <ul style={{ listStyle: 'none', marginBottom: '2rem' }}>
                                {[
                                    `All ${totalModels} screening models`,
                                    '150 stock scans per month',
                                    'US & Thai market coverage',
                                    'Advanced backtesting',
                                    'PDF reports',
                                    'Email support',
                                ].map((item, i) => (
                                    <li key={i} style={{
                                        padding: '0.6rem 0',
                                        borderBottom: '1px solid var(--border)',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '0.75rem',
                                    }}>
                                        <span style={{ color: 'var(--success)', fontSize: '1.1rem' }}>✓</span> {item}
                                    </li>
                                ))}
                            </ul>
                            <Link href={`/sign-up?plan=pro-${isAnnual ? 'annual' : 'monthly'}`} style={{
                                display: 'block',
                                textAlign: 'center',
                                textDecoration: 'none',
                                padding: '1rem',
                                background: 'var(--card)',
                                color: 'var(--foreground)',
                                border: '3px solid var(--border)',
                                boxShadow: '4px 4px 0 var(--border)',
                                fontWeight: '700',
                                fontSize: '1rem',
                            }}>
                                Get Pro {isAnnual ? '— Save 2 Months' : ''}
                            </Link>
                        </div>

                        {/* Unlimited Plan */}
                        <div style={{
                            padding: '2.5rem',
                            background: 'var(--primary)',
                            color: 'var(--primary-foreground)',
                            border: '3px solid var(--border)',
                            boxShadow: '5px 5px 0 var(--border)',
                            position: 'relative',
                        }}>
                            <div style={{
                                position: 'absolute',
                                top: '-14px',
                                right: '24px',
                                background: 'var(--foreground)',
                                color: 'var(--background)',
                                padding: '0.35rem 1rem',
                                fontSize: '0.75rem',
                                fontWeight: '700',
                                border: '2px solid var(--border)',
                            }}>
                                MOST POPULAR
                            </div>
                            <h3 style={{ fontSize: '1.5rem', fontWeight: '800', marginBottom: '0.5rem' }}>Unlimited</h3>
                            <p style={{ opacity: 0.85, marginBottom: '1.5rem', fontSize: '0.9rem' }}>
                                For power users & professionals
                            </p>
                            <div style={{ marginBottom: '0.5rem' }}>
                                <span style={{ fontSize: '3.5rem', fontWeight: '900' }}>
                                    ${isAnnual ? '82' : '99'}
                                </span>
                                <span style={{ fontSize: '1.1rem', fontWeight: '500', opacity: 0.8 }}>/mo</span>
                            </div>
                            {isAnnual && (
                                <p style={{ fontSize: '0.85rem', opacity: 0.85, marginBottom: '1rem' }}>
                                    <s>$1,188</s> → <strong>$990/year</strong> (Save $198)
                                </p>
                            )}
                            <p style={{
                                fontWeight: '700',
                                marginBottom: '1.5rem',
                                fontSize: '1rem',
                                padding: '0.5rem',
                                background: 'rgba(255,255,255,0.15)',
                                border: '2px solid rgba(255,255,255,0.3)',
                            }}>
                                ∞ Unlimited stock scans
                            </p>
                            <ul style={{ listStyle: 'none', marginBottom: '2rem' }}>
                                {[
                                    `All ${totalModels} screening models`,
                                    'Unlimited stock scans',
                                    'US & Thai market coverage',
                                    'Advanced backtesting',
                                    'Priority support',
                                    isAnnual ? 'Early access to new features' : 'PDF reports',
                                ].map((item, i) => (
                                    <li key={i} style={{
                                        padding: '0.6rem 0',
                                        borderBottom: '1px solid rgba(255,255,255,0.2)',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '0.75rem',
                                    }}>
                                        <span style={{ fontSize: '1.1rem' }}>✓</span> {item}
                                    </li>
                                ))}
                            </ul>
                            <Link href={`/sign-up?plan=unlimited-${isAnnual ? 'annual' : 'monthly'}`} style={{
                                display: 'block',
                                textAlign: 'center',
                                textDecoration: 'none',
                                padding: '1rem',
                                background: 'var(--foreground)',
                                color: 'var(--background)',
                                border: '3px solid var(--foreground)',
                                boxShadow: '4px 4px 0 rgba(0,0,0,0.3)',
                                fontWeight: '700',
                                fontSize: '1rem',
                            }}>
                                Get Unlimited {isAnnual ? '— Best Value' : ''}
                            </Link>
                        </div>
                    </div>

                    {/* Money-back guarantee */}
                    <p style={{
                        textAlign: 'center',
                        marginTop: '2rem',
                        color: 'var(--muted-foreground)',
                        fontSize: '0.9rem',
                    }}>
                        💳 Secure payment • 🔒 Cancel anytime • ⚡ 7-day money-back guarantee
                    </p>
                </div>
            </section>

            {/* Final CTA Section */}
            <section style={{
                padding: '5rem 2rem',
                background: 'var(--foreground)',
                color: 'var(--background)',
                textAlign: 'center',
            }}>
                <div style={{ maxWidth: '700px', margin: '0 auto' }}>
                    <h2 style={{
                        fontSize: '2.5rem',
                        fontWeight: '900',
                        marginBottom: '1rem',
                    }}>
                        Your Competition is Already Using This
                    </h2>
                    <p style={{
                        fontSize: '1.1rem',
                        opacity: 0.8,
                        marginBottom: '2rem',
                    }}>
                        Every day you wait, you're leaving alpha on the table. Join {totalModels} models,
                        thousands of signals, and make smarter trades.
                    </p>
                    <Link href="/sign-up" style={{
                        display: 'inline-block',
                        textDecoration: 'none',
                        padding: '1.125rem 3rem',
                        background: 'var(--primary)',
                        color: 'var(--primary-foreground)',
                        border: '3px solid var(--background)',
                        boxShadow: '5px 5px 0 var(--background)',
                        fontWeight: '800',
                        fontSize: '1.15rem',
                    }}>
                        Get Started Now →
                    </Link>
                    <p style={{ marginTop: '1rem', fontSize: '0.875rem', opacity: 0.6 }}>
                        7-day money-back guarantee • Cancel anytime
                    </p>
                </div>
            </section>

            {/* Footer */}
            <footer style={{
                padding: '2rem',
                background: 'var(--card)',
                borderTop: '3px solid var(--border)',
                textAlign: 'center',
            }}>
                <p style={{ color: 'var(--muted-foreground)', fontSize: '0.875rem' }}>
                    © 2024 QuantStack. Professional stock screening for serious traders.
                </p>
            </footer>
        </div>
    );
}
