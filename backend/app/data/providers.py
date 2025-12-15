"""
Data Providers - Abstract interface and implementations for multiple data sources
Supports: yfinance, pandas_datareader, alpha_vantage, and more
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Import SETSMART provider (late import to avoid circular dependency)
try:
    from .setsmart_provider import SetsmartProvider
    SETSMART_AVAILABLE = True
except ImportError:
    SETSMART_AVAILABLE = False


class DataProvider(ABC):
    """Base class for all data providers"""
    
    @abstractmethod
    def get_price_data(
        self, 
        ticker: str, 
        period: str = "1y",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Get price data for a ticker
        Returns DataFrame with columns: date, open, high, low, close, volume
        """
        pass
    
    @abstractmethod
    def get_fundamental_data(self, ticker: str) -> Optional[Dict]:
        """
        Get fundamental data for a ticker
        Returns dict with financial metrics
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is available/configured"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get provider name"""
        pass


class YahooFinanceProvider(DataProvider):
    """Yahoo Finance provider using yfinance"""
    
    def __init__(self):
        try:
            import yfinance as yf
            self.yf = yf
            self._available = True
        except ImportError:
            logger.warning("yfinance not available")
            self._available = False
    
    def get_name(self) -> str:
        return "yfinance"
    
    def is_available(self) -> bool:
        return self._available
    
    def get_price_data(
        self, 
        ticker: str, 
        period: str = "1y",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        if not self._available:
            return None
        
        try:
            stock = self.yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval)
            
            if df.empty:
                return None
            
            # Standardize column names
            df = df.reset_index()
            df.columns = [c.lower().replace(' ', '_') for c in df.columns]
            
            # Ensure we have required columns
            if 'date' not in df.columns and 'datetime' in df.columns:
                df['date'] = df['datetime']
            
            return df
            
        except Exception as e:
            logger.debug(f"yfinance error for {ticker}: {e}")
            return None
    
    def get_fundamental_data(self, ticker: str) -> Optional[Dict]:
        if not self._available:
            return None
        
        try:
            stock = self.yf.Ticker(ticker)
            info = stock.info
            
            if not info or info.get('regularMarketPrice') is None:
                return None
            
            # Extract relevant fields
            data = {
                "ticker": ticker,
                "name": info.get('shortName', ticker),
                "price": info.get('regularMarketPrice'),
                "market_cap": info.get('marketCap'),
                
                # Valuation
                "pe_ratio": info.get('trailingPE'),
                "forward_pe": info.get('forwardPE'),
                "pb_ratio": info.get('priceToBook'),
                "ps_ratio": info.get('priceToSalesTrailing12Months'),
                "peg_ratio": info.get('pegRatio'),
                
                # Enterprise Value metrics (for EV/EBITDA model)
                "enterprise_value": info.get('enterpriseValue'),
                "ev_to_ebitda": info.get('enterpriseToEbitda'),
                "ev_to_revenue": info.get('enterpriseToRevenue'),
                
                # EBITDA and Cash Flow (for EV/EBITDA and FCF models)
                "ebitda": info.get('ebitda'),
                "ebitda_margins": info.get('ebitdaMargins'),
                "total_revenue": info.get('totalRevenue'),
                "total_debt": info.get('totalDebt'),
                "total_cash": info.get('totalCash'),
                "free_cash_flow": info.get('freeCashflow'),
                "operating_cash_flow": info.get('operatingCashflow'),
                
                # Profitability
                "roe": info.get('returnOnEquity'),
                "roa": info.get('returnOnAssets'),
                "profit_margin": info.get('profitMargins'),
                "operating_margin": info.get('operatingMargins'),
                "gross_margin": info.get('grossMargins'),
                
                # Growth
                "revenue_growth": info.get('revenueGrowth'),
                "earnings_growth": info.get('earningsGrowth'),
                "earnings_quarterly_growth": info.get('earningsQuarterlyGrowth'),
                
                # Dividends
                "dividend_yield": info.get('dividendYield'),
                "payout_ratio": info.get('payoutRatio'),
                
                # Financial Health
                "debt_to_equity": info.get('debtToEquity'),
                "current_ratio": info.get('currentRatio'),
                "quick_ratio": info.get('quickRatio'),
                
                # Per Share
                "eps": info.get('trailingEps'),
                "forward_eps": info.get('forwardEps'),
                "book_value": info.get('bookValue'),
                
                # Other
                "beta": info.get('beta'),
                "52w_high": info.get('fiftyTwoWeekHigh'),
                "52w_low": info.get('fiftyTwoWeekLow'),
                "50d_avg": info.get('fiftyDayAverage'),
                "200d_avg": info.get('twoHundredDayAverage'),
                "avg_volume": info.get('averageVolume'),
            }
            
            return data
            
        except Exception as e:
            logger.debug(f"yfinance fundamental error for {ticker}: {e}")
            return None


class PandasDataReaderProvider(DataProvider):
    """Pandas DataReader provider (supports multiple sources)"""
    
    def __init__(self, source: str = "yahoo"):
        """
        Args:
            source: Data source ('yahoo', 'stooq', 'fred', etc.)
        """
        self.source = source
        try:
            import pandas_datareader.data as web
            self.web = web
            self._available = True
        except ImportError:
            logger.warning("pandas_datareader not available")
            self._available = False
    
    def get_name(self) -> str:
        return f"pandas_datareader_{self.source}"
    
    def is_available(self) -> bool:
        return self._available
    
    def get_price_data(
        self, 
        ticker: str, 
        period: str = "1y",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        if not self._available:
            return None
        
        try:
            from datetime import datetime, timedelta
            
            # Convert period to date range
            end = datetime.now()
            if period == "1y":
                start = end - timedelta(days=365)
            elif period == "6mo":
                start = end - timedelta(days=180)
            elif period == "3mo":
                start = end - timedelta(days=90)
            elif period == "1mo":
                start = end - timedelta(days=30)
            else:
                start = end - timedelta(days=365)
            
            df = self.web.DataReader(ticker, self.source, start, end)
            
            if df.empty:
                return None
            
            # Standardize column names
            df = df.reset_index()
            df.columns = [c.lower().replace(' ', '_') for c in df.columns]
            
            # Ensure we have required columns
            if 'date' not in df.columns and 'datetime' in df.columns:
                df['date'] = df['datetime']
            
            return df
            
        except Exception as e:
            logger.debug(f"pandas_datareader error for {ticker}: {e}")
            return None
    
    def get_fundamental_data(self, ticker: str) -> Optional[Dict]:
        # pandas_datareader primarily for price data
        # For fundamentals, we'd need additional sources
        return None


class AlphaVantageProvider(DataProvider):
    """Alpha Vantage provider (requires API key)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or None
        try:
            from alpha_vantage.timeseries import TimeSeries
            from alpha_vantage.fundamentaldata import FundamentalData
            self.TimeSeries = TimeSeries
            self.FundamentalData = FundamentalData
            self._available = self.api_key is not None
        except ImportError:
            logger.warning("alpha_vantage not available")
            self._available = False
    
    def get_name(self) -> str:
        return "alpha_vantage"
    
    def is_available(self) -> bool:
        return self._available and self.api_key is not None
    
    def get_price_data(
        self, 
        ticker: str, 
        period: str = "1y",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        if not self.is_available():
            return None
        
        try:
            ts = self.TimeSeries(key=self.api_key, output_format='pandas')
            
            # Map interval
            av_interval = 'daily'
            if interval == "1h":
                av_interval = '60min'
            elif interval == "5m":
                av_interval = '5min'
            
            data, meta_data = ts.get_daily_adjusted(symbol=ticker, outputsize='full')
            
            if data.empty:
                return None
            
            # Standardize column names
            data = data.reset_index()
            data.columns = [c.lower().replace(' ', '_').replace('.', '_') for c in data.columns]
            
            # Rename columns to match expected format
            column_mapping = {
                'date': 'date',
                '1_open': 'open',
                '2_high': 'high',
                '3_low': 'low',
                '4_close': 'close',
                '5_adjusted_close': 'close',
                '6_volume': 'volume'
            }
            
            for old, new in column_mapping.items():
                if old in data.columns:
                    data[new] = data[old]
            
            if 'date' not in data.columns:
                return None
            
            return data
            
        except Exception as e:
            logger.debug(f"alpha_vantage error for {ticker}: {e}")
            return None
    
    def get_fundamental_data(self, ticker: str) -> Optional[Dict]:
        if not self.is_available():
            return None
        
        try:
            fd = self.FundamentalData(key=self.api_key, output_format='pandas')
            
            # Get company overview
            overview, _ = fd.get_company_overview(symbol=ticker)
            
            if overview.empty:
                return None
            
            # Convert to dict format
            data = {
                "ticker": ticker,
                "name": overview.get('Name', {}).iloc[0] if 'Name' in overview.columns else ticker,
                "price": float(overview.get('52WeekHigh', {}).iloc[0]) if '52WeekHigh' in overview.columns else None,
                "market_cap": float(overview.get('MarketCapitalization', {}).iloc[0]) if 'MarketCapitalization' in overview.columns else None,
                "pe_ratio": float(overview.get('PERatio', {}).iloc[0]) if 'PERatio' in overview.columns else None,
                "pb_ratio": float(overview.get('PriceToBookRatio', {}).iloc[0]) if 'PriceToBookRatio' in overview.columns else None,
                "peg_ratio": float(overview.get('PEGRatio', {}).iloc[0]) if 'PEGRatio' in overview.columns else None,
                "profit_margin": float(overview.get('ProfitMargin', {}).iloc[0]) if 'ProfitMargin' in overview.columns else None,
                "roe": float(overview.get('ReturnOnEquityTTM', {}).iloc[0]) if 'ReturnOnEquityTTM' in overview.columns else None,
                "eps": float(overview.get('EPS', {}).iloc[0]) if 'EPS' in overview.columns else None,
                "dividend_yield": float(overview.get('DividendYield', {}).iloc[0]) if 'DividendYield' in overview.columns else None,
                "52w_high": float(overview.get('52WeekHigh', {}).iloc[0]) if '52WeekHigh' in overview.columns else None,
                "52w_low": float(overview.get('52WeekLow', {}).iloc[0]) if '52WeekLow' in overview.columns else None,
            }
            
            return data
            
        except Exception as e:
            logger.debug(f"alpha_vantage fundamental error for {ticker}: {e}")
            return None


def get_available_providers() -> List[DataProvider]:
    """Get list of all available data providers"""
    providers = []
    
    import os
    
    # SETSMART (Official SET Thailand data - prioritize for Thai stocks)
    if SETSMART_AVAILABLE:
        setsmart_key = os.getenv("SETSMART_API_KEY")
        if setsmart_key:
            setsmart_provider = SetsmartProvider(api_key=setsmart_key)
            if setsmart_provider.is_available():
                providers.append(setsmart_provider)
                logger.info("SETSMART provider enabled for Thai stocks")
    
    # Yahoo Finance (default, most reliable for US stocks)
    yf_provider = YahooFinanceProvider()
    if yf_provider.is_available():
        providers.append(yf_provider)
    
    # Pandas DataReader
    pdr_provider = PandasDataReaderProvider()
    if pdr_provider.is_available():
        providers.append(pdr_provider)
    
    # Alpha Vantage (if API key is set)
    av_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if av_key:
        av_provider = AlphaVantageProvider(api_key=av_key)
        if av_provider.is_available():
            providers.append(av_provider)
    
    return providers

