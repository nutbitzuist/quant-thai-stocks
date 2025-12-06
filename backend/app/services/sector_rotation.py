"""
Sector Rotation Analyzer
Identifies strongest and weakest sectors for rotation strategies
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import defaultdict
import pandas as pd
import numpy as np
from datetime import datetime

from app.data.universe import Sector, get_universe


@dataclass
class SectorAnalysis:
    """Analysis for a single sector"""
    sector: str
    avg_return_1w: float
    avg_return_1m: float
    avg_return_3m: float
    relative_strength: float
    momentum_score: float
    stock_count: int
    top_stocks: List[Dict]
    bottom_stocks: List[Dict]
    rank: int


class SectorRotationAnalyzer:
    """
    Analyzes sector performance and identifies rotation opportunities.
    
    Based on the business cycle and relative strength:
    1. Calculate sector returns over multiple timeframes
    2. Rank sectors by momentum
    3. Identify rotation opportunities (strong sectors to buy, weak to avoid)
    """
    
    def __init__(self):
        self.sectors = [s.value for s in Sector]
    
    def analyze_sector_rotation(
        self,
        price_data: Dict[str, pd.DataFrame],
        universe: str = "sp500"
    ) -> Dict:
        """
        Analyze sector rotation for a given universe.
        
        Returns sector rankings and rotation recommendations.
        """
        # Get universe stocks with sector info
        stocks = get_universe(universe)
        
        # Group tickers by sector
        sector_tickers = defaultdict(list)
        ticker_to_sector = {}
        for stock in stocks:
            sector_tickers[stock.sector.value].append(stock.ticker)
            ticker_to_sector[stock.ticker] = stock.sector.value
        
        # Calculate returns for each stock
        stock_returns = {}
        for ticker, df in price_data.items():
            if df is None or len(df) < 63:  # Need at least 3 months
                continue
            
            close = df['close']
            returns = {
                '1w': (close.iloc[-1] / close.iloc[-5] - 1) * 100 if len(df) >= 5 else 0,
                '1m': (close.iloc[-1] / close.iloc[-21] - 1) * 100 if len(df) >= 21 else 0,
                '3m': (close.iloc[-1] / close.iloc[-63] - 1) * 100 if len(df) >= 63 else 0,
            }
            stock_returns[ticker] = returns
        
        # Calculate sector averages
        sector_results = []
        for sector, tickers in sector_tickers.items():
            returns_1w = []
            returns_1m = []
            returns_3m = []
            stock_data = []
            
            for ticker in tickers:
                if ticker in stock_returns:
                    r = stock_returns[ticker]
                    returns_1w.append(r['1w'])
                    returns_1m.append(r['1m'])
                    returns_3m.append(r['3m'])
                    
                    stock_data.append({
                        'ticker': ticker.replace('.BK', ''),
                        'return_1w': round(r['1w'], 2),
                        'return_1m': round(r['1m'], 2),
                        'return_3m': round(r['3m'], 2)
                    })
            
            if not returns_1m:
                continue
            
            avg_1w = np.mean(returns_1w)
            avg_1m = np.mean(returns_1m)
            avg_3m = np.mean(returns_3m)
            
            # Momentum score (weighted average of returns)
            momentum = avg_1w * 0.3 + avg_1m * 0.4 + avg_3m * 0.3
            
            # Sort stocks by 1m return
            stock_data.sort(key=lambda x: x['return_1m'], reverse=True)
            
            sector_results.append(SectorAnalysis(
                sector=sector,
                avg_return_1w=avg_1w,
                avg_return_1m=avg_1m,
                avg_return_3m=avg_3m,
                relative_strength=momentum,
                momentum_score=momentum,
                stock_count=len(stock_data),
                top_stocks=stock_data[:5],
                bottom_stocks=stock_data[-5:],
                rank=0  # Will be set below
            ))
        
        # Rank sectors by momentum
        sector_results.sort(key=lambda x: x.momentum_score, reverse=True)
        for i, sr in enumerate(sector_results):
            sr.rank = i + 1
        
        # Rotation recommendations
        strong_sectors = [sr for sr in sector_results if sr.rank <= 3]
        weak_sectors = [sr for sr in sector_results if sr.rank > len(sector_results) - 3]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "universe": universe,
            "total_sectors": len(sector_results),
            "rotation_recommendation": {
                "overweight": [s.sector for s in strong_sectors],
                "underweight": [s.sector for s in weak_sectors],
                "summary": f"Rotate into {strong_sectors[0].sector if strong_sectors else 'N/A'}, "
                          f"avoid {weak_sectors[-1].sector if weak_sectors else 'N/A'}"
            },
            "sector_rankings": [
                {
                    "rank": sr.rank,
                    "sector": sr.sector,
                    "momentum_score": round(sr.momentum_score, 2),
                    "return_1w": round(sr.avg_return_1w, 2),
                    "return_1m": round(sr.avg_return_1m, 2),
                    "return_3m": round(sr.avg_return_3m, 2),
                    "stock_count": sr.stock_count,
                    "top_stocks": sr.top_stocks[:3],
                    "signal": "BUY" if sr.rank <= 3 else "SELL" if sr.rank > len(sector_results) - 3 else "HOLD"
                }
                for sr in sector_results
            ]
        }


# Singleton
_analyzer = None

def get_sector_analyzer() -> SectorRotationAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = SectorRotationAnalyzer()
    return _analyzer
