
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import pandas as pd
import numpy as np
from app.data.fetcher import get_fetcher
from app.data.universe import get_stock_info

router = APIRouter()

class AnalysisResponse(BaseModel):
    ticker: str
    name: str
    price: float
    currency: str
    score: int  # 0-100
    recommendation: str  # Strong Buy, Buy, Hold, Sell, Strong Sell
    summary: str
    metrics: Dict[str, Any]
    technicals: Dict[str, Any]
    checkpoints: List[Dict[str, Any]]  # List of {label, status: pass/fail/neutral, value}

def calculate_score(fund: Dict, tech: pd.DataFrame) -> Dict:
    """
    Calculate a quantitative score (0-100) based on fundamentals and technicals.
    Returns details including score, recommendation, and checkpoint details.
    """
    score = 50  # Start neutral
    checkpoints = []
    
    # helper to add checkpoint
    def add_cp(label, condition, weight, value_str):
        nonlocal score
        status = "neutral"
        if condition is True:
            score += weight
            status = "pass"
        elif condition is False:
            score -= weight
            status = "fail"
        
        checkpoints.append({
            "label": label,
            "status": status,
            "value": value_str
        })

    # --- VALUATION (Max +/- 30) ---
    pe = fund.get('pe_ratio')
    if pe and pe > 0:
        if pe < 15:
            add_cp("Low P/E Ratio", True, 10, f"{pe:.2f}")
        elif pe > 40:
            add_cp("High P/E Ratio", False, 10, f"{pe:.2f}")
        else:
            add_cp("Moderate P/E", None, 0, f"{pe:.2f}")
    
    pb = fund.get('pb_ratio')
    if pb and pb > 0:
        if pb < 1.5:
            add_cp("Low P/B Ratio", True, 5, f"{pb:.2f}")
        elif pb > 5:
            add_cp("High P/B Ratio", False, 5, f"{pb:.2f}")

    # --- GROWTH (Max +/- 20) ---
    rev_growth = fund.get('revenue_growth')
    if rev_growth:
        if rev_growth > 0.15: # >15%
            add_cp("Strong Revenue Growth", True, 10, f"{rev_growth*100:.1f}%")
        elif rev_growth < 0:
            add_cp("Negative Revenue Growth", False, 10, f"{rev_growth*100:.1f}%")
            
    earn_growth = fund.get('earnings_growth')
    if earn_growth:
        if earn_growth > 0.15:
             add_cp("Strong Earnings Growth", True, 10, f"{earn_growth*100:.1f}%")

    # --- PROFITABILITY (Max +/- 20) ---
    roe = fund.get('roe')
    if roe:
        if roe > 0.15:
            add_cp("High ROE", True, 10, f"{roe*100:.1f}%")
        elif roe < 0.05:
            add_cp("Low ROE", False, 5, f"{roe*100:.1f}%")
            
    margin = fund.get('profit_margin')
    if margin:
        if margin > 0.20:
             add_cp("High Profit Margin", True, 10, f"{margin*100:.1f}%")
        elif margin < 0:
             add_cp("Unprofitable", False, 10, f"{margin*100:.1f}%")

    # --- TECHNICALS (Max +/- 30) ---
    if tech is not None and not tech.empty:
        latest = tech.iloc[-1]
        
        # Trend
        sma200 = latest.get('sma_200')
        close = latest['close']
        if sma200 and close > sma200:
             add_cp("Above 200 SMA (Long term trend)", True, 10, "Bullish")
        elif sma200 and close < sma200:
             add_cp("Below 200 SMA (Long term trend)", False, 10, "Bearish")
             
        # RSI
        rsi = latest.get('rsi')
        if rsi:
            if rsi < 30:
                add_cp("Oversold (RSI < 30)", True, 10, f"{rsi:.1f}")
            elif rsi > 70:
                add_cp("Overbought (RSI > 70)", False, 10, f"{rsi:.1f}")
            else:
                 add_cp("Neutral RSI", None, 0, f"{rsi:.1f}")

        # MACD
        macd = latest.get('macd')
        signal = latest.get('macd_signal')
        if macd and signal:
            if macd > signal:
                add_cp("MACD Bullish Crossover", True, 10, "Bullish")
            else:
                add_cp("MACD Bearish Crossover", False, 10, "Bearish")

    # Normalize Score 0-100
    score = max(0, min(100, score))
    
    # Recommendation
    rec = "Hold"
    if score >= 80: rec = "Strong Buy"
    elif score >= 65: rec = "Buy"
    elif score <= 20: rec = "Strong Sell"
    elif score <= 35: rec = "Sell"

    summary = f"The stock has a quant score of {score}/100 based on our automated analysis. "
    if score >= 65:
        summary += "It shows strong fundamentals and/or positive technical momentum."
    elif score <= 35:
        summary += "It is currently showing weakness in valuation, growth, or technical trend."
    else:
        summary += "It presents a mixed picture with offsetting factors."

    return {
        "score": score,
        "recommendation": rec,
        "summary": summary,
        "checkpoints": checkpoints
    }

@router.get("/{ticker}", response_model=AnalysisResponse)
async def analyze_stock(ticker: str):
    """
    Analyze a stock by its ticker.
    Fetcher fundamental and technical data, computes a score.
    """
    ticker = ticker.upper()
    # Normalize BK ticker if needed (simple heuristic, can be improved)
    if not ticker.endswith(".BK") and not ticker.isalpha(): 
        # assume user might type just "DELTA" for thai stock if they are in thai context? 
        # For now, strict matching, or try to find in universe.
        pass
        
    stock_info = get_stock_info(ticker)
    name = stock_info.name if stock_info else ticker
    market = stock_info.market.value if stock_info else "Unknown"
    
    fetcher = get_fetcher()
    
    # 1. Get Fundamentals
    fund = fetcher.get_fundamental_data(ticker)
    if not fund:
        # Try appending .BK if not found and looks like a potential Thai stock name?
        # Or just fail. Let's try to be robust.
        if not ticker.endswith(".BK"):
             fund_bk = fetcher.get_fundamental_data(f"{ticker}.BK")
             if fund_bk:
                 ticker = f"{ticker}.BK"
                 fund = fund_bk
                 
    if not fund:
         raise HTTPException(status_code=404, detail=f"Could not fetch fundamental data for {ticker}")

    # 2. Get Price & Technicals
    price = fetcher.get_price_data(ticker, period="1y")
    technicals = None
    tech_dict = {}
    
    current_price = fund.get('price', 0.0)
    
    if price is not None and not price.empty:
        price = fetcher.calculate_technicals(price)
        technicals = price
        latest = price.iloc[-1]
        if current_price == 0:
            current_price = latest['close']
            
        tech_dict = {
            "close": float(latest['close']),
            "sma_200": float(latest['sma_200']) if not pd.isna(latest['sma_200']) else None,
            "rsi": float(latest['rsi']) if not pd.isna(latest['rsi']) else None,
            "macd": float(latest['macd']) if not pd.isna(latest['macd']) else None,
            "return_1y": float((latest['close'] / price.iloc[0]['close'] - 1) * 100)
        }

    # 3. Calculate Score
    analysis = calculate_score(fund, technicals)
    
    return AnalysisResponse(
        ticker=ticker,
        name=fund.get('name', name),
        price=current_price,
        currency="THB" if ticker.endswith(".BK") else "USD",
        score=analysis["score"],
        recommendation=analysis["recommendation"],
        summary=analysis["summary"],
        metrics=fund,
        technicals=tech_dict,
        checkpoints=analysis["checkpoints"]
    )
