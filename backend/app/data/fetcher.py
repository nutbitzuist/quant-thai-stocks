"""
Data Fetcher - Handles all data retrieval from multiple data sources
With caching, parallel fetching, fallback providers, and detailed error logging
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import time
import os

from .providers import (
    DataProvider, 
    YahooFinanceProvider, 
    PandasDataReaderProvider,
    AlphaVantageProvider,
    get_available_providers
)

logger = logging.getLogger(__name__)


class DataFetcher:
    """
    Fetches price and fundamental data from multiple data sources
    Features:
    - Multiple data providers with automatic fallback
    - Caching to reduce API calls
    - Parallel fetching for speed
    - Detailed error logging
    - Technical indicator calculations
    """
    
    def __init__(
        self, 
        cache_minutes: int = 30, 
        max_workers: int = 10,
        providers: Optional[List[str]] = None,
        fallback_enabled: bool = True
    ):
        """
        Args:
            cache_minutes: Cache duration in minutes
            max_workers: Max parallel workers for bulk fetching
            providers: List of provider names to use (in order). 
                      If None, uses all available providers.
            fallback_enabled: If True, tries next provider on failure
        """
        self.cache_minutes = cache_minutes
        self.max_workers = max_workers
        self.fallback_enabled = fallback_enabled
        self._price_cache: Dict[str, Tuple[datetime, pd.DataFrame]] = {}
        self._fundamental_cache: Dict[str, Tuple[datetime, Dict]] = {}
        self._errors: List[Dict] = []
        
        # Initialize providers
        self._providers: List[DataProvider] = []
        self._initialize_providers(providers)
        
        if not self._providers:
            logger.warning("No data providers available! Install yfinance or other data libraries.")
    
    def _initialize_providers(self, provider_names: Optional[List[str]]):
        """Initialize data providers based on configuration"""
        all_providers = get_available_providers()
        
        if provider_names:
            # Use specified providers in order
            provider_map = {p.get_name(): p for p in all_providers}
            for name in provider_names:
                if name in provider_map:
                    self._providers.append(provider_map[name])
                else:
                    logger.warning(f"Provider '{name}' not available, skipping")
        else:
            # Use all available providers, with yfinance first
            yf_providers = [p for p in all_providers if p.get_name() == "yfinance"]
            other_providers = [p for p in all_providers if p.get_name() != "yfinance"]
            self._providers = yf_providers + other_providers
        
        logger.info(f"Initialized {len(self._providers)} data provider(s): {[p.get_name() for p in self._providers]}")
    
    def get_providers(self) -> List[str]:
        """Get list of active provider names"""
        return [p.get_name() for p in self._providers]
    
    def get_errors(self) -> List[Dict]:
        """Get list of recent errors for debugging"""
        return self._errors[-50:]  # Last 50 errors
    
    def clear_errors(self):
        """Clear error log"""
        self._errors = []
    
    def _log_error(self, ticker: str, operation: str, error: str):
        """Log an error for debugging"""
        self._errors.append({
            "timestamp": datetime.now().isoformat(),
            "ticker": ticker,
            "operation": operation,
            "error": str(error)
        })
        logger.error(f"[{ticker}] {operation}: {error}")
    
    def get_price_data(
        self, 
        ticker: str, 
        period: str = "1y",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Get price data for a single ticker
        Tries multiple providers with fallback if enabled
        Returns DataFrame with columns: date, open, high, low, close, volume
        """
        cache_key = f"{ticker}_{period}_{interval}"
        
        # Check cache
        if cache_key in self._price_cache:
            cached_time, cached_data = self._price_cache[cache_key]
            if datetime.now() - cached_time < timedelta(minutes=self.cache_minutes):
                return cached_data
        
        # Try each provider in order
        last_error = None
        for provider in self._providers:
            try:
                df = provider.get_price_data(ticker, period, interval)
                
                if df is not None and not df.empty:
                    # Validate required columns
                    required_cols = ['close']
                    if all(col in df.columns for col in required_cols):
                        # Cache the result
                        self._price_cache[cache_key] = (datetime.now(), df)
                        return df
                    else:
                        logger.warning(f"Provider {provider.get_name()} returned incomplete data for {ticker}")
                
            except Exception as e:
                last_error = e
                self._log_error(ticker, f"get_price_data({provider.get_name()})", str(e))
                
                # If fallback disabled, stop on first error
                if not self.fallback_enabled:
                    break
        
        # All providers failed
        if last_error:
            self._log_error(ticker, "get_price_data", f"All providers failed. Last error: {last_error}")
        else:
            self._log_error(ticker, "get_price_data", "No data returned from any provider")
        
        return None
    
    def get_fundamental_data(self, ticker: str) -> Optional[Dict]:
        """
        Get fundamental data for a single ticker
        Tries multiple providers with fallback if enabled
        Returns dict with P/E, P/B, ROE, margins, etc.
        """
        # Check cache
        if ticker in self._fundamental_cache:
            cached_time, cached_data = self._fundamental_cache[ticker]
            if datetime.now() - cached_time < timedelta(minutes=self.cache_minutes):
                return cached_data
        
        # Try each provider in order
        last_error = None
        for provider in self._providers:
            try:
                data = provider.get_fundamental_data(ticker)
                
                if data is not None and data.get('price') is not None:
                    # Cache the result
                    self._fundamental_cache[ticker] = (datetime.now(), data)
                    return data
                
            except Exception as e:
                last_error = e
                self._log_error(ticker, f"get_fundamental_data({provider.get_name()})", str(e))
                
                # If fallback disabled, stop on first error
                if not self.fallback_enabled:
                    break
        
        # All providers failed
        if last_error:
            self._log_error(ticker, "get_fundamental_data", f"All providers failed. Last error: {last_error}")
        else:
            self._log_error(ticker, "get_fundamental_data", "No data returned from any provider")
        
        return None
    
    def get_bulk_price_data(
        self, 
        tickers: List[str], 
        period: str = "1y",
        progress_callback = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch price data for multiple tickers in parallel
        Returns dict mapping ticker -> DataFrame
        """
        results = {}
        total = len(tickers)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_ticker = {
                executor.submit(self.get_price_data, ticker, period): ticker 
                for ticker in tickers
            }
            
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                completed += 1
                
                try:
                    data = future.result()
                    if data is not None:
                        results[ticker] = data
                except Exception as e:
                    self._log_error(ticker, "bulk_price_fetch", str(e))
                
                if progress_callback:
                    progress_callback(completed, total, ticker)
        
        return results
    
    def get_bulk_fundamental_data(
        self, 
        tickers: List[str],
        progress_callback = None
    ) -> pd.DataFrame:
        """
        Fetch fundamental data for multiple tickers
        Returns DataFrame with one row per ticker
        """
        results = []
        total = len(tickers)
        completed = 0
        
        # Use fewer workers for fundamentals (rate limiting)
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_ticker = {
                executor.submit(self.get_fundamental_data, ticker): ticker 
                for ticker in tickers
            }
            
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                completed += 1
                
                try:
                    data = future.result()
                    if data is not None:
                        results.append(data)
                except Exception as e:
                    self._log_error(ticker, "bulk_fundamental_fetch", str(e))
                
                if progress_callback:
                    progress_callback(completed, total, ticker)
        
        if not results:
            return pd.DataFrame()
        
        return pd.DataFrame(results)
    
    def calculate_technicals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to price DataFrame"""
        if df is None or df.empty:
            return df
        
        df = df.copy()
        close = df['close']
        high = df['high']
        low = df['low']
        volume = df['volume']
        
        # Moving Averages
        df['sma_20'] = close.rolling(window=20).mean()
        df['sma_50'] = close.rolling(window=50).mean()
        df['sma_200'] = close.rolling(window=200).mean()
        df['ema_12'] = close.ewm(span=12, adjust=False).mean()
        df['ema_26'] = close.ewm(span=26, adjust=False).mean()
        
        # RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss.replace(0, np.nan)
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # Bollinger Bands
        df['bb_middle'] = df['sma_20']
        bb_std = close.rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        
        # ATR (Average True Range)
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df['atr'] = tr.rolling(window=14).mean()
        
        # Volume indicators
        df['volume_sma'] = volume.rolling(window=20).mean()
        df['volume_ratio'] = volume / df['volume_sma']
        
        # Price momentum
        df['return_1d'] = close.pct_change(1) * 100
        df['return_5d'] = close.pct_change(5) * 100
        df['return_20d'] = close.pct_change(20) * 100
        df['return_60d'] = close.pct_change(60) * 100
        
        # 52-week high/low
        df['high_52w'] = high.rolling(window=252).max()
        df['low_52w'] = low.rolling(window=252).min()
        df['pct_from_high'] = (close / df['high_52w'] - 1) * 100
        df['pct_from_low'] = (close / df['low_52w'] - 1) * 100
        
        return df


# Singleton instance
_fetcher_instance = None


def get_fetcher() -> DataFetcher:
    """Get the singleton DataFetcher instance"""
    from ..config import settings
    
    global _fetcher_instance
    if _fetcher_instance is None:
        providers = settings.data_providers if settings.data_providers else None
        _fetcher_instance = DataFetcher(
            cache_minutes=settings.data_cache_minutes,
            max_workers=settings.max_workers,
            providers=providers,
            fallback_enabled=settings.data_fallback_enabled
        )
    return _fetcher_instance
