"""
Model Documentation
Detailed explanations of each model's logic, parameters, and usage
"""

MODEL_DOCS = {
    "rsi_reversal": {
        "name": "RSI Reversal",
        "category": "Technical",
        "summary": "Mean reversion strategy using Relative Strength Index",
        "description": """
The RSI Reversal model identifies overbought and oversold conditions using the Relative Strength Index (RSI), 
a momentum oscillator developed by J. Welles Wilder Jr.

**How it works:**
- RSI measures the speed and magnitude of recent price changes
- Values range from 0 to 100
- RSI below 30 indicates oversold (potential buy)
- RSI above 70 indicates overbought (potential sell)

**Best used for:**
- Range-bound markets
- Mean reversion strategies
- Short-term trading (days to weeks)

**Caution:**
- In strong trends, RSI can stay overbought/oversold for extended periods
- Works best when combined with other indicators
        """,
        "parameters": {
            "rsi_period": {
                "default": 14,
                "description": "Number of periods for RSI calculation",
                "range": "5-30"
            },
            "oversold": {
                "default": 30,
                "description": "Threshold for oversold condition (buy signal)",
                "range": "20-40"
            },
            "overbought": {
                "default": 70,
                "description": "Threshold for overbought condition (sell signal)",
                "range": "60-80"
            }
        },
        "signals": {
            "buy": "RSI crosses below oversold threshold",
            "sell": "RSI crosses above overbought threshold"
        },
        "references": [
            "Wilder, J.W. (1978). New Concepts in Technical Trading Systems"
        ]
    },
    
    "macd_crossover": {
        "name": "MACD Crossover",
        "category": "Technical",
        "summary": "Trend-following momentum indicator using moving average convergence/divergence",
        "description": """
MACD (Moving Average Convergence Divergence) is a trend-following momentum indicator that shows 
the relationship between two exponential moving averages.

**How it works:**
- MACD Line = 12-day EMA - 26-day EMA
- Signal Line = 9-day EMA of MACD Line
- Histogram = MACD Line - Signal Line

**Buy Signal:** MACD crosses above Signal Line (bullish crossover)
**Sell Signal:** MACD crosses below Signal Line (bearish crossover)

**Best used for:**
- Trend identification
- Momentum confirmation
- Medium-term trading

**Caution:**
- Lagging indicator (signals come after price moves)
- Can generate false signals in choppy markets
        """,
        "parameters": {
            "fast_period": {"default": 12, "description": "Fast EMA period"},
            "slow_period": {"default": 26, "description": "Slow EMA period"},
            "signal_period": {"default": 9, "description": "Signal line EMA period"},
            "lookback_days": {"default": 5, "description": "Days to look back for crossover"}
        },
        "signals": {
            "buy": "MACD crosses above signal line",
            "sell": "MACD crosses below signal line"
        },
        "references": [
            "Appel, G. (1979). The Moving Average Convergence-Divergence Trading Method"
        ]
    },
    
    "minervini_trend": {
        "name": "Minervini Trend Template",
        "category": "Technical",
        "summary": "Stage 2 uptrend identification using Mark Minervini's SEPA criteria",
        "description": """
The Minervini Trend Template identifies stocks in Stage 2 (advancing) uptrends using strict technical criteria 
developed by US Investing Champion Mark Minervini.

**The 8 Criteria:**
1. Price above 150-day and 200-day moving average
2. 150-day MA above 200-day MA
3. 200-day MA trending up for at least 1 month
4. 50-day MA above both 150-day and 200-day MA
5. Price above 50-day MA
6. Price at least 25% above 52-week low
7. Price within 25% of 52-week high
8. Relative Strength Rating > 70

**Best used for:**
- Growth stock selection
- Trend following strategies
- Position trading (weeks to months)

**Key insight:**
Stocks that meet all 8 criteria are in a confirmed Stage 2 uptrend with 
institutional accumulation - the optimal time to buy growth stocks.
        """,
        "parameters": {
            "min_above_52w_low_pct": {"default": 25, "description": "Minimum % above 52-week low"},
            "max_below_52w_high_pct": {"default": 25, "description": "Maximum % below 52-week high"},
            "min_rs_rating": {"default": 70, "description": "Minimum Relative Strength rating"}
        },
        "signals": {
            "buy": "Stock meets 8+ of the criteria",
            "sell": "Stock fails 5+ criteria (breaking down)"
        },
        "references": [
            "Minervini, M. (2013). Trade Like a Stock Market Wizard",
            "Minervini, M. (2017). Think & Trade Like a Champion"
        ]
    },
    
    "darvas_box": {
        "name": "Darvas Box",
        "category": "Technical",
        "summary": "Breakout trading from consolidation boxes",
        "description": """
The Darvas Box method was developed by Nicolas Darvas, a dancer who made $2 million 
in the stock market in the 1950s.

**How it works:**
1. Stock makes a new 52-week high
2. Price consolidates in a "box" (trading range)
3. Box top = High that hasn't been exceeded for 3+ days
4. Box bottom = Lowest low since box top formed
5. BUY when price breaks above box top with high volume
6. STOP LOSS at box bottom

**Best used for:**
- Breakout trading
- Momentum stocks
- Growth investing

**Key insight:**
The consolidation (box) represents accumulation by smart money before 
the next leg up. Breakouts on volume confirm institutional buying.
        """,
        "parameters": {
            "box_days": {"default": 20, "description": "Days to look for box formation"},
            "volume_multiplier": {"default": 1.5, "description": "Volume must be X times average"},
            "require_52w_high": {"default": True, "description": "Require stock near 52-week high"}
        },
        "signals": {
            "buy": "Price breaks above box top with 1.5x average volume",
            "sell": "Price breaks below box bottom"
        },
        "references": [
            "Darvas, N. (1960). How I Made $2,000,000 in the Stock Market"
        ]
    },
    
    "turtle_trading": {
        "name": "Turtle Trading",
        "category": "Technical",
        "summary": "Channel breakout system from the legendary Turtle experiment",
        "description": """
The Turtle Trading system was taught by Richard Dennis to a group of novice traders 
in the 1980s, proving that trading could be taught systematically.

**System 2 Rules (used here):**
- BUY: Price exceeds 55-day high
- SELL: Price breaks 20-day low
- Position sizing based on ATR (volatility)

**Key concepts:**
- Let winners run (trailing stop at 20-day low)
- Cut losses short (strict stop-loss)
- Trade with the trend
- Add to winning positions (pyramiding)

**Best used for:**
- Trend following
- Systematic trading
- Multiple markets/assets

**Important:**
The Turtles made most of their money from a few big trends. 
Most trades were small losses, but the winners more than compensated.
        """,
        "parameters": {
            "entry_period": {"default": 55, "description": "Days for entry breakout"},
            "exit_period": {"default": 20, "description": "Days for exit breakdown"},
            "atr_period": {"default": 20, "description": "ATR period for volatility"}
        },
        "signals": {
            "buy": "Price exceeds 55-day high",
            "sell": "Price breaks 20-day low"
        },
        "references": [
            "Faith, C. (2003). Way of the Turtle",
            "Covel, M. (2007). The Complete TurtleTrader"
        ]
    },
    
    "elder_triple_screen": {
        "name": "Elder Triple Screen",
        "category": "Technical",
        "summary": "Multi-timeframe system with Force Index for pullback entries",
        "description": """
Dr. Alexander Elder's Triple Screen combines multiple timeframes and indicators 
to filter trades and improve timing.

**The Three Screens:**
1. **Weekly Trend (Screen 1):** Identify trend direction using EMA slope
2. **Daily Momentum (Screen 2):** Use Force Index for timing
3. **Entry (Screen 3):** Use trailing stops for precise entry

**Force Index = (Close - Previous Close) × Volume**
- Positive: Bulls in control
- Negative: Bears in control
- Divergences signal potential reversals

**Trading Logic:**
- In uptrend: Buy when Force Index dips negative (pullback)
- In downtrend: Sell when Force Index spikes positive (rally)

**Best used for:**
- Swing trading
- Pullback entries in trends
- Risk management
        """,
        "parameters": {
            "trend_period": {"default": 26, "description": "EMA period for trend"},
            "force_period": {"default": 13, "description": "Force Index smoothing"},
            "atr_multiplier": {"default": 2.0, "description": "ATR multiple for stops"}
        },
        "signals": {
            "buy": "Uptrend + Force Index turning positive from negative",
            "sell": "Downtrend + Force Index turning negative from positive"
        },
        "references": [
            "Elder, A. (1993). Trading for a Living",
            "Elder, A. (2002). Come Into My Trading Room"
        ]
    },
    
    "canslim": {
        "name": "CANSLIM",
        "category": "Fundamental",
        "summary": "William O'Neil's growth stock selection methodology",
        "description": """
CANSLIM is a growth investing system developed by William O'Neil, founder of 
Investor's Business Daily. It combines fundamental and technical factors.

**The 7 Criteria:**
- **C** - Current Quarterly Earnings: Up 25%+ from same quarter last year
- **A** - Annual Earnings Growth: 25%+ growth for past 5 years
- **N** - New Products/Management/Highs: Innovation driving growth
- **S** - Supply and Demand: Look for volume on up days
- **L** - Leader or Laggard: RS Rating > 80 (top 20%)
- **I** - Institutional Sponsorship: Quality fund ownership
- **M** - Market Direction: Bull market confirmation

**Best used for:**
- Growth stock investing
- Long-term positions
- Bull markets

**Key insight:**
Historically, stocks that doubled or tripled shared these characteristics 
BEFORE their big moves. The system identifies them early.
        """,
        "parameters": {
            "min_quarterly_eps_growth": {"default": 25, "description": "Min quarterly EPS growth %"},
            "min_annual_eps_growth": {"default": 25, "description": "Min annual EPS growth %"},
            "min_rs_rating": {"default": 80, "description": "Min Relative Strength rating"},
            "min_roe": {"default": 17, "description": "Min Return on Equity %"}
        },
        "signals": {
            "buy": "Stock meets 5+ of the 7 CANSLIM criteria",
            "sell": "Stock fails multiple criteria or breaks down technically"
        },
        "references": [
            "O'Neil, W. (1988). How to Make Money in Stocks"
        ]
    },
    
    "value_composite": {
        "name": "Value Composite",
        "category": "Fundamental",
        "summary": "Multi-factor value scoring using classic valuation metrics",
        "description": """
The Value Composite model ranks stocks based on traditional value metrics, 
identifying potentially undervalued companies.

**Metrics Used:**
- P/E Ratio (35% weight) - Lower is better
- P/B Ratio (30% weight) - Lower is better
- P/S Ratio (20% weight) - Lower is better
- Dividend Yield (15% weight) - Higher is better

**Scoring:**
Each metric is ranked across the universe, then weighted and combined.
Top 20% = Buy, Bottom 20% = Sell

**Best used for:**
- Value investing
- Income-focused portfolios
- Defensive positioning

**Caution:**
Cheap stocks can be cheap for good reasons (value traps).
Combine with quality metrics for better results.
        """,
        "parameters": {
            "pe_weight": {"default": 0.35, "description": "P/E ratio weight"},
            "pb_weight": {"default": 0.30, "description": "P/B ratio weight"},
            "ps_weight": {"default": 0.20, "description": "P/S ratio weight"},
            "div_weight": {"default": 0.15, "description": "Dividend yield weight"}
        },
        "signals": {
            "buy": "Top 20% composite value score",
            "sell": "Bottom 20% composite value score"
        },
        "references": [
            "Graham, B. (1949). The Intelligent Investor",
            "Greenblatt, J. (2005). The Little Book That Beats the Market"
        ]
    },
    
    "quality_score": {
        "name": "Quality Score",
        "category": "Fundamental",
        "summary": "Identify high-quality companies based on profitability and financial health",
        "description": """
The Quality Score model identifies companies with strong fundamentals 
that are likely to be good long-term investments.

**Quality Metrics:**
- Return on Equity (ROE) - 25% weight
- Return on Assets (ROA) - 15% weight
- Profit Margin - 20% weight
- Operating Margin - 15% weight
- Debt to Equity (inverse) - 15% weight
- Current Ratio - 10% weight

**Philosophy:**
High-quality companies tend to:
- Maintain profitability through economic cycles
- Have sustainable competitive advantages (moats)
- Generate consistent cash flows
- Outperform over the long term

**Best used for:**
- Long-term investing
- Defensive portfolios
- Quality-at-reasonable-price strategies
        """,
        "parameters": {
            "roe_weight": {"default": 0.25, "description": "ROE weight"},
            "roa_weight": {"default": 0.15, "description": "ROA weight"},
            "profit_margin_weight": {"default": 0.20, "description": "Profit margin weight"},
            "debt_weight": {"default": 0.15, "description": "Debt/Equity weight (inverse)"}
        },
        "signals": {
            "buy": "Top 20% quality score",
            "sell": "Bottom 20% quality score"
        },
        "references": [
            "Novy-Marx, R. (2013). The Quality Dimension of Value Investing",
            "Asness, C. et al. (2014). Quality Minus Junk"
        ]
    },
    
    "piotroski_f": {
        "name": "Piotroski F-Score",
        "category": "Fundamental",
        "summary": "9-point financial strength scoring system",
        "description": """
The Piotroski F-Score was developed by Stanford professor Joseph Piotroski 
to identify financially strong value stocks.

**The 9 Criteria (1 point each):**

*Profitability (4 points):*
1. Positive Return on Assets (ROA)
2. Positive Operating Cash Flow
3. ROA higher than previous year
4. Cash flow > Net income (earnings quality)

*Leverage & Liquidity (3 points):*
5. Lower debt ratio than previous year
6. Higher current ratio than previous year
7. No new share dilution

*Operating Efficiency (2 points):*
8. Higher gross margin than previous year
9. Higher asset turnover than previous year

**Interpretation:**
- F-Score 7-9: Strong financials (BUY)
- F-Score 4-6: Average financials (HOLD)
- F-Score 0-3: Weak financials (SELL/AVOID)

**Best used for:**
- Deep value investing
- Avoiding value traps
- Small-cap screening
        """,
        "parameters": {
            "buy_threshold": {"default": 7, "description": "Minimum F-Score for buy signal"},
            "sell_threshold": {"default": 3, "description": "Maximum F-Score for sell signal"}
        },
        "signals": {
            "buy": "F-Score >= 7 (strong financials)",
            "sell": "F-Score <= 3 (weak financials)"
        },
        "references": [
            "Piotroski, J. (2000). Value Investing: The Use of Historical Financial Statement Information"
        ]
    },
    
    # ========== NEW MODELS ==========
    
    "magic_formula": {
        "name": "Magic Formula",
        "category": "Fundamental",
        "summary": "Joel Greenblatt's value + quality combination",
        "description": """
Joel Greenblatt's Magic Formula from "The Little Book That Beats the Market."
Combines Earnings Yield (cheapness) with Return on Capital (quality).
Buy stocks with best combined rank. Simple, systematic, effective.
        """,
        "parameters": {
            "earnings_yield_weight": {"default": 0.5, "description": "Weight for earnings yield"},
            "roc_weight": {"default": 0.5, "description": "Weight for return on capital"}
        },
        "signals": {"buy": "Top 20% combined rank", "sell": "Bottom 20%"},
        "references": ["Greenblatt, J. (2005). The Little Book That Beats the Market"]
    },
    
    "dividend_aristocrats": {
        "name": "Dividend Aristocrats",
        "category": "Fundamental",
        "summary": "Quality dividend stocks with sustainable payouts",
        "description": """
High-quality dividend payers with sustainable payouts.
Looks for: Good yield (2-6%), reasonable payout ratio (<80%), strong ROE.
Avoids very high yields (often distress signals).
        """,
        "parameters": {
            "min_dividend_yield": {"default": 2.0, "description": "Minimum dividend yield %"},
            "max_payout_ratio": {"default": 80, "description": "Maximum payout ratio %"}
        },
        "signals": {"buy": "Sustainable dividend + quality", "sell": "Unsustainable payout"},
        "references": ["S&P Dividend Aristocrats methodology"]
    },
    
    "earnings_momentum": {
        "name": "Earnings Momentum",
        "category": "Fundamental",
        "summary": "Positive earnings revisions and growth acceleration",
        "description": """
Stocks with improving earnings outlook. Forward EPS > Trailing EPS.
Earnings momentum tends to persist. Buy positive revisions early.
        """,
        "parameters": {
            "min_eps_growth": {"default": 10, "description": "Minimum EPS growth %"},
            "min_revenue_growth": {"default": 5, "description": "Minimum revenue growth %"}
        },
        "signals": {"buy": "Positive revisions", "sell": "Negative revisions"},
        "references": ["Post-earnings announcement drift research"]
    },
    
    "garp": {
        "name": "GARP",
        "category": "Fundamental",
        "summary": "Growth at Reasonable Price - Peter Lynch's PEG approach",
        "description": """
Peter Lynch's approach: find growth but don't overpay.
PEG = P/E / Growth Rate. PEG < 1 = undervalued growth.
        """,
        "parameters": {
            "max_peg": {"default": 1.5, "description": "Maximum PEG ratio"},
            "min_growth": {"default": 10, "description": "Minimum growth %"}
        },
        "signals": {"buy": "PEG < 1.5", "sell": "PEG > 2.5"},
        "references": ["Lynch, P. (1989). One Up on Wall Street"]
    },
    
    "altman_z": {
        "name": "Altman Z-Score",
        "category": "Fundamental",
        "summary": "Bankruptcy prediction - avoid distressed companies",
        "description": """
Predicts bankruptcy probability. Z > 2.99 = Safe. Z < 1.81 = Distress.
Uses working capital, retained earnings, EBIT, market cap, and sales ratios.
        """,
        "parameters": {
            "safe_threshold": {"default": 2.99, "description": "Safe zone threshold"},
            "distress_threshold": {"default": 1.81, "description": "Distress zone threshold"}
        },
        "signals": {"buy": "Safe zone", "sell": "Distress zone"},
        "references": ["Altman, E. (1968). Financial Ratios and Corporate Bankruptcy"]
    },
    
    "bollinger_squeeze": {
        "name": "Bollinger Squeeze",
        "category": "Technical",
        "summary": "Volatility contraction breakout",
        "description": """
When Bollinger Bands narrow (squeeze), volatility is low.
Big moves often follow. Buy breakout above upper band with volume.
        """,
        "parameters": {
            "bb_period": {"default": 20, "description": "Bollinger Band period"},
            "squeeze_percentile": {"default": 20, "description": "Squeeze threshold"}
        },
        "signals": {"buy": "Breakout above upper band", "sell": "Breakdown below lower band"},
        "references": ["Bollinger, J. (2001). Bollinger on Bollinger Bands"]
    },
    
    "adx_trend": {
        "name": "ADX Trend Strength",
        "category": "Technical",
        "summary": "Average Directional Index for trend strength",
        "description": """
Measures trend strength (not direction). ADX > 25 = strong trend.
+DI > -DI = uptrend. -DI > +DI = downtrend. Buy strong uptrends.
        """,
        "parameters": {
            "adx_period": {"default": 14, "description": "ADX calculation period"},
            "strong_trend": {"default": 25, "description": "Strong trend threshold"}
        },
        "signals": {"buy": "Strong uptrend (ADX>25, +DI>-DI)", "sell": "Strong downtrend"},
        "references": ["Wilder, J.W. (1978). New Concepts in Technical Trading Systems"]
    },
    
    "keltner_channel": {
        "name": "Keltner Channel",
        "category": "Technical",
        "summary": "ATR-based channel breakout",
        "description": """
Similar to Bollinger Bands but uses ATR. EMA + ATR*multiplier.
Breakout above channel = strong buy. Works well for trending markets.
        """,
        "parameters": {
            "ema_period": {"default": 20, "description": "EMA period"},
            "atr_multiplier": {"default": 2.0, "description": "ATR multiplier"}
        },
        "signals": {"buy": "Price above upper channel", "sell": "Price below lower channel"},
        "references": ["Chester Keltner's original 1960 work"]
    },
    
    "volume_profile": {
        "name": "Volume Profile",
        "category": "Technical",
        "summary": "Support/resistance from volume concentration",
        "description": """
Analyzes where most volume occurs at different price levels.
POC (Point of Control) = highest volume price. Value Area = 70% of volume.
Buy near support (HVN below), sell near resistance (HVN above).
        """,
        "parameters": {
            "lookback_days": {"default": 60, "description": "Days to analyze"},
            "value_area_pct": {"default": 70, "description": "Value area percentage"}
        },
        "signals": {"buy": "Breakout above value area", "sell": "Breakdown below value area"},
        "references": ["Market Profile and Volume Profile trading"]
    },
    
    "dual_ema": {
        "name": "Dual EMA Filter",
        "category": "Technical",
        "summary": "Price above EMA15 and EMA50 confirms uptrend",
        "description": """
Simple but effective: Price above both EMA15 and EMA50 = strong uptrend.
EMA15 above EMA50 = bullish structure. Both EMAs rising = momentum.
        """,
        "parameters": {
            "fast_ema": {"default": 15, "description": "Fast EMA period"},
            "slow_ema": {"default": 50, "description": "Slow EMA period"}
        },
        "signals": {"buy": "Price above both EMAs, structure bullish", "sell": "Price below both EMAs"},
        "references": ["Standard EMA crossover systems"]
    },
    
    # ========== QUANTITATIVE/STATISTICAL MODELS ==========
    
    "mean_reversion": {
        "name": "Mean Reversion Z-Score",
        "category": "Quantitative",
        "summary": "Statistical arbitrage based on price deviation from mean",
        "description": """
The Mean Reversion model uses Z-Score to identify stocks that have deviated 
significantly from their historical mean price.

**How it works:**
- Calculate rolling mean and standard deviation of price
- Z-Score = (Current Price - Mean) / Standard Deviation
- Z < -2: Price is 2+ standard deviations below mean (oversold)
- Z > 2: Price is 2+ standard deviations above mean (overbought)

**Statistical Basis:**
Based on the principle that prices tend to revert to their mean over time.
Extreme deviations are statistically unlikely to persist.

**Half-Life Estimation:**
The model estimates how quickly prices revert using autocorrelation analysis.
Shorter half-life = faster mean reversion = better trading opportunity.

**Best used for:**
- Statistical arbitrage
- Range-bound markets
- Short-term mean reversion trades
- Pairs trading setups

**Caution:**
- Trending markets can stay "extreme" for extended periods
- Works best in stable, range-bound conditions
- Combine with trend filters for better results
        """,
        "parameters": {
            "lookback_period": {"default": 20, "description": "Rolling window for mean/std calculation"},
            "z_buy_threshold": {"default": -2.0, "description": "Z-Score threshold for buy signal"},
            "z_sell_threshold": {"default": 2.0, "description": "Z-Score threshold for sell signal"},
            "min_data_points": {"default": 50, "description": "Minimum data points required"}
        },
        "signals": {
            "buy": "Z-Score < -2 (price significantly below mean)",
            "sell": "Z-Score > 2 (price significantly above mean)"
        },
        "references": [
            "Avellaneda, M. & Lee, J.H. (2010). Statistical Arbitrage in the US Equities Market",
            "Pole, A. (2007). Statistical Arbitrage"
        ]
    },
    
    "pairs_trading": {
        "name": "Pairs Trading Setup",
        "category": "Quantitative",
        "summary": "Correlation-based statistical arbitrage between related stocks",
        "description": """
Pairs Trading identifies stocks that are highly correlated but have temporarily diverged.
When the spread between correlated pairs deviates significantly, trade the convergence.

**How it works:**
1. Calculate correlation matrix for all stocks
2. Find best correlated pair for each stock (correlation > 0.7)
3. Calculate spread Z-Score between the pair
4. Trade when spread deviates beyond threshold

**Trading Logic:**
- If spread Z < -2: Stock underperformed vs pair → BUY stock
- If spread Z > 2: Stock outperformed vs pair → SELL stock
- Expect spread to revert to historical relationship

**Key Metrics:**
- Correlation: How closely the pair moves together
- Spread Z-Score: Current deviation from normal relationship
- Relative Performance: Recent return difference

**Best used for:**
- Market-neutral strategies
- Hedged positions
- Sector-relative trades
- Reducing market risk

**Caution:**
- Correlations can break down (regime change)
- Requires both legs to execute properly
- Transaction costs matter for tight spreads
        """,
        "parameters": {
            "correlation_period": {"default": 60, "description": "Days for correlation calculation"},
            "min_correlation": {"default": 0.7, "description": "Minimum correlation for valid pair"},
            "spread_z_threshold": {"default": 2.0, "description": "Z-Score threshold for signal"},
            "lookback_period": {"default": 20, "description": "Spread Z-Score lookback"}
        },
        "signals": {
            "buy": "Spread Z < -2 (underperformed vs correlated pair)",
            "sell": "Spread Z > 2 (outperformed vs correlated pair)"
        },
        "references": [
            "Gatev, E., Goetzmann, W. & Rouwenhorst, K. (2006). Pairs Trading",
            "Vidyamurthy, G. (2004). Pairs Trading: Quantitative Methods and Analysis"
        ]
    },
    
    "factor_momentum": {
        "name": "Factor Momentum",
        "category": "Quantitative",
        "summary": "Momentum of momentum - trade accelerating trends",
        "description": """
Factor Momentum captures the "momentum of momentum" - stocks where the momentum 
itself is accelerating or decelerating.

**How it works:**
- Calculate short-term momentum (20-day return)
- Calculate long-term momentum (60-day return)
- Measure momentum acceleration (change in momentum)
- Buy when momentum is positive AND accelerating
- Sell when momentum is negative AND decelerating

**Why it works:**
Research shows that momentum factor returns are themselves persistent.
Accelerating momentum indicates strengthening trend conviction.
Decelerating momentum warns of potential reversal.

**Momentum Quality:**
The model also measures momentum quality - how consistent the trend is.
Higher quality = more days moving in trend direction.

**Best used for:**
- Trend following with timing
- Avoiding momentum crashes
- Position sizing based on conviction
- Systematic momentum strategies

**Key insight:**
Traditional momentum can suffer "momentum crashes" when trends reverse.
Factor momentum helps identify when momentum is strengthening vs weakening.
        """,
        "parameters": {
            "short_momentum_period": {"default": 20, "description": "Short-term momentum period"},
            "long_momentum_period": {"default": 60, "description": "Long-term momentum period"},
            "momentum_change_period": {"default": 10, "description": "Period for acceleration calculation"},
            "acceleration_threshold": {"default": 0.5, "description": "Threshold for significant acceleration"}
        },
        "signals": {
            "buy": "Positive momentum + accelerating",
            "sell": "Negative momentum + decelerating"
        },
        "references": [
            "Ehsani, S. & Linnainmaa, J. (2020). Factor Momentum and the Momentum Factor",
            "Gupta, T. & Kelly, B. (2019). Factor Momentum Everywhere"
        ]
    },
    
    "volatility_breakout": {
        "name": "Volatility Breakout",
        "category": "Quantitative",
        "summary": "ATR-based breakout entries with volatility squeeze detection",
        "description": """
The Volatility Breakout model identifies stocks breaking out of their normal 
volatility range, especially after periods of low volatility (squeeze).

**How it works:**
- Calculate ATR (Average True Range) for volatility measurement
- Define breakout levels: Previous Close ± (ATR × Multiplier)
- Detect volatility squeeze (ATR in bottom percentile)
- Signal when price breaks through levels

**Volatility Squeeze:**
When volatility contracts (squeeze), it often precedes a big move.
The model identifies these setups for higher probability breakouts.

**Breakout Confirmation:**
- Volume confirmation: Breakout with 1.5x average volume
- ATR expansion: Volatility increasing on breakout
- Price follow-through: Sustained move beyond breakout level

**Best used for:**
- Breakout trading
- Volatility expansion strategies
- Pre-earnings setups
- Range contraction patterns

**Key metrics:**
- ATR %: Volatility as percentage of price
- Volatility Percentile: Where current vol sits vs history
- Volume Ratio: Current vs average volume
        """,
        "parameters": {
            "atr_period": {"default": 14, "description": "ATR calculation period"},
            "atr_multiplier": {"default": 2.0, "description": "ATR multiplier for breakout levels"},
            "squeeze_period": {"default": 20, "description": "Period for squeeze detection"},
            "squeeze_threshold": {"default": 0.7, "description": "Percentile threshold for squeeze"},
            "volume_confirmation": {"default": True, "description": "Require volume confirmation"}
        },
        "signals": {
            "buy": "Price breaks above upper level (especially from squeeze)",
            "sell": "Price breaks below lower level"
        },
        "references": [
            "Bollinger, J. (2001). Bollinger on Bollinger Bands",
            "Keltner Channel and ATR-based systems"
        ]
    },
    
    # NEW FUNDAMENTAL MODELS
    "ev_ebitda": {
        "name": "EV/EBITDA Screen",
        "category": "Fundamental",
        "summary": "Enterprise Value to EBITDA - Better than P/E for cross-company comparisons",
        "description": """
**EV/EBITDA Screen** uses Enterprise Value to EBITDA ratio for valuation analysis.

**Why EV/EBITDA is better than P/E:**
- Capital structure neutral (accounts for debt)
- Less affected by accounting differences (depreciation methods)
- Better for comparing companies across industries
- Excludes non-cash charges

**Formula:**
- EV = Market Cap + Total Debt - Cash
- EV/EBITDA = Enterprise Value / EBITDA

**Interpretation:**
- Low EV/EBITDA (< 10): Potentially undervalued
- Average (10-15): Fair value
- High (> 15): Potentially overvalued

**Best used for:**
- Comparing companies with different capital structures
- M&A analysis (acquirers look at EV/EBITDA)
- Capital-intensive industries
        """,
        "parameters": {
            "max_ev_ebitda": {"default": 15.0, "description": "Maximum EV/EBITDA for BUY signal"},
            "min_ev_ebitda": {"default": 0.0, "description": "Minimum EV/EBITDA (avoid negative)"},
            "min_ebitda_margin": {"default": 10.0, "description": "Minimum EBITDA margin %"},
            "prefer_low_debt": {"default": True, "description": "Prefer companies with low debt"},
            "debt_to_ebitda_max": {"default": 4.0, "description": "Maximum Debt/EBITDA ratio"}
        },
        "signals": {
            "buy": "Low EV/EBITDA with healthy margins and manageable debt",
            "sell": "High EV/EBITDA or negative EBITDA"
        },
        "references": [
            "Damodaran, A. - Investment Valuation",
            "Enterprise Value analysis in M&A"
        ]
    },
    
    "fcf_yield": {
        "name": "FCF Yield",
        "category": "Fundamental",
        "summary": "Free Cash Flow Yield - Focus on actual cash generation",
        "description": """
**Free Cash Flow Yield** identifies stocks generating strong cash relative to price.

**Why FCF matters:**
- Cash is harder to manipulate than earnings
- Shows actual cash generation ability
- Better indicator of dividend sustainability
- Warren Buffett's preferred metric

**Formula:**
- FCF = Operating Cash Flow - Capital Expenditures
- FCF Yield = (FCF / Market Cap) × 100

**Interpretation:**
- High FCF Yield (> 8%): Potentially undervalued cash generator
- Average (4-8%): Fair value
- Low (< 4%): May be overvalued or capital-intensive

**Key metrics:**
- FCF Margin: FCF as % of revenue
- FCF Conversion: FCF / Net Income (> 100% is excellent)
- CapEx Ratio: CapEx as % of Operating Cash Flow
        """,
        "parameters": {
            "min_fcf_yield": {"default": 5.0, "description": "Minimum FCF yield % for BUY"},
            "min_fcf_margin": {"default": 5.0, "description": "Minimum FCF margin %"},
            "require_positive_fcf": {"default": True, "description": "Require positive FCF"},
            "max_capex_ratio": {"default": 50.0, "description": "Maximum CapEx as % of OCF"}
        },
        "signals": {
            "buy": "High FCF yield with consistent cash generation",
            "sell": "Negative FCF or very low yield"
        },
        "references": [
            "Buffett, W. - Owner Earnings concept",
            "Free Cash Flow analysis in value investing"
        ]
    },
    
    "momentum_value": {
        "name": "Momentum + Value Combo",
        "category": "Fundamental",
        "summary": "Factor investing combining value metrics with price momentum",
        "description": """
**Momentum + Value Combo** combines two proven investment factors.

**Factor Investing Research:**
- Value and Momentum are two of the most robust factors
- Combining factors can improve risk-adjusted returns
- Value stocks with momentum outperform pure value or pure momentum

**Value Component:**
- P/E Ratio (lower is better)
- P/B Ratio (lower is better)
- P/S Ratio (lower is better)
- Dividend Yield (higher is better)

**Momentum Component:**
- 6-month price momentum
- 12-month price momentum
- Recent trend confirmation (1-3 months)

**Why it works:**
- Value identifies cheap stocks
- Momentum confirms the market is recognizing value
- Avoids "value traps" (cheap stocks that stay cheap)
        """,
        "parameters": {
            "value_weight": {"default": 0.5, "description": "Weight for value score (0-1)"},
            "momentum_weight": {"default": 0.5, "description": "Weight for momentum score (0-1)"},
            "max_pe": {"default": 25.0, "description": "Maximum P/E for value score"},
            "max_pb": {"default": 5.0, "description": "Maximum P/B for value score"},
            "min_momentum_6m": {"default": 0.0, "description": "Minimum 6-month momentum %"},
            "min_momentum_12m": {"default": 0.0, "description": "Minimum 12-month momentum %"}
        },
        "signals": {
            "buy": "Undervalued stock with positive momentum",
            "sell": "Overvalued stock with negative momentum"
        },
        "references": [
            "Asness, C. - Value and Momentum Everywhere",
            "Fama-French Factor Research"
        ]
    }
}


def get_model_documentation(model_id: str) -> dict:
    """Get documentation for a specific model"""
    return MODEL_DOCS.get(model_id, {})


def get_all_model_docs() -> dict:
    """Get all model documentation"""
    return MODEL_DOCS


def get_model_list_with_summaries() -> list:
    """Get list of models with summaries for display"""
    return [
        {
            "id": model_id,
            "name": doc["name"],
            "category": doc["category"],
            "summary": doc["summary"]
        }
        for model_id, doc in MODEL_DOCS.items()
    ]
