from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import Response
from typing import Dict, Any, List, Optional
import yfinance as yf
import pandas as pd
import numpy as np
from pydantic import BaseModel
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from ...data.fetcher import get_fetcher
from ...data.universe import get_stock_info

router = APIRouter()

class AnalysisResponse(BaseModel):
    ticker: str
    name: str
    price: float
    currency: str
    score: int  # 0-100
    recommendation: str  # Strong Buy, Buy, Hold, Sell, Strong Sell
    summary: str
    metrics: Dict[str, Any]  # Now includes solvency, cash_flow, forward_looking
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

    # --- SOLVENCY (Max +/- 10) ---
    de = fund.get('debt_to_equity')
    if de:
        # yfinance returns D/E as strictly value (e.g. 150 for 1.5 ratio? or 1.5? Usually 0-200+)
        # Checking typical yf values: often it's percentage, e.g. 80.5 means 0.805 or 80.5%? 
        # Usually yf returns ratio * 100. So 100 = 1.0 D/E.
        if de < 100: # < 1.0 D/E
             add_cp("Healthy Debt/Equity", True, 5, f"{de:.1f}%")
        elif de > 200: # > 2.0 D/E
             add_cp("High Debt Level", False, 5, f"{de:.1f}%")
             
    current_ratio = fund.get('current_ratio')
    if current_ratio:
        if current_ratio > 1.5:
             add_cp("Strong Liquidity (Current Ratio)", True, 5, f"{current_ratio:.2f}")
        elif current_ratio < 1.0:
             add_cp("Weak Liquidity (Current Ratio)", False, 5, f"{current_ratio:.2f}")

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

def create_pdf_report(data: Dict[str, Any]) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph(f"Stock Analysis Report: {data['ticker']}", styles['Title']))
    story.append(Spacer(1, 12))
    
    # Summary
    story.append(Paragraph(f"Price: {data['price']} {data['currency']}", styles['Heading2']))
    story.append(Paragraph(f"Score: {data['score']}/100 - {data['recommendation']}", styles['Heading2']))
    story.append(Paragraph(data['summary'], styles['BodyText']))
    story.append(Spacer(1, 12))

    # Metrics Table
    story.append(Paragraph("Key Fundamentals", styles['Heading2']))
    metrics_data = [["Metric", "Value"]]
    m = data['metrics']
    
    # Helper to clean values
    def fmt(val, is_pct=False):
        if val is None: return "-"
        if is_pct: return f"{val*100:.2f}%"
        return f"{val:.2f}"

    metrics_data.append(["Evaluation", ""])
    metrics_data.append(["P/E Ratio", fmt(m.get('pe_ratio'))])
    metrics_data.append(["Forward P/E", fmt(m.get('forward_pe'))])
    metrics_data.append(["PEG Ratio", fmt(m.get('peg_ratio'))])
    metrics_data.append(["P/B Ratio", fmt(m.get('pb_ratio'))])
    
    metrics_data.append(["Growth & Profitability", ""])
    metrics_data.append(["Revenue Growth", fmt(m.get('revenue_growth'), True)])
    metrics_data.append(["Profit Margin", fmt(m.get('profit_margin'), True)])
    metrics_data.append(["ROE", fmt(m.get('roe'), True)])
    
    metrics_data.append(["Financial Health", ""])
    metrics_data.append(["Debt/Equity", fmt(m.get('debt_to_equity'))])
    metrics_data.append(["Current Ratio", fmt(m.get('current_ratio'))])
    metrics_data.append(["Free Cash Flow", fmt(m.get('free_cash_flow'))])

    t = Table(metrics_data, colWidths=[200, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    # Technicals
    story.append(Paragraph("Technical Indicators", styles['Heading2']))
    tech = data['technicals']
    tech_data = [
        ["Indicator", "Value"],
        ["RSI (14)", fmt(tech.get('rsi'))],
        ["MACD", fmt(tech.get('macd'))],
        ["SMA 200", fmt(tech.get('sma_200'))],
        ["1Y Return", fmt(tech.get('return_1y'), True)]
    ]
    t_tech = Table(tech_data, colWidths=[200, 100])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(t_tech)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

@router.get("/{ticker}/pdf")
async def get_analysis_pdf(ticker: str):
    # Reuse the analysis logic
    # Note: efficient way is to separate logic, but for now calling the endpoint function directly involves request context
    # So we'll just re-run the logic or refactor. Re-running logic is safer for statelessness here.
    
    # Fetch data (logic duplicated from analyze_stock to ensure clean data for PDF)
    # Ideally should refactor analyze_stock to return dict, then wrap in router
    data_response = await analyze_stock(ticker)
    data = data_response.dict()
    
    pdf_buffer = create_pdf_report(data)
    
    headers = {
        'Content-Disposition': f'attachment; filename="{ticker}_analysis.pdf"'
    }
    return Response(content=pdf_buffer.getvalue(), media_type="application/pdf", headers=headers)

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
