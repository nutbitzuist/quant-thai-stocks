"""
SETSMART API Provider - Official SET (Stock Exchange of Thailand) data source
Provides high-quality data for Thai stocks including EOD prices and fundamentals

API Documentation: https://www.setsmart.com (login required)
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging
import time

logger = logging.getLogger(__name__)


class SetsmartProvider:
    """
    SETSMART API provider for official SET Thai stock data
    
    Features:
    - EOD prices with open/high/low/close/volume
    - Fundamental data: P/E, P/B, ROE, dividend yield, market cap
    - Automatic ticker format conversion (.BK -> SET format)
    - Retry with exponential backoff for rate limiting
    
    Note: Requires SETSMART subscription and API key
    """
    
    BASE_URL = "https://www.setsmart.com/api/v1"
    
    def __init__(self, api_key: str):
        """
        Initialize SETSMART provider
        
        Args:
            api_key: SETSMART API key from your account
        """
        self.api_key = api_key
        self._available = bool(api_key)
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        self._max_retries = 3
        self._retry_delay = 1.0
    
    def get_name(self) -> str:
        return "setsmart"
    
    def is_available(self) -> bool:
        return self._available
    
    def _convert_ticker(self, ticker: str) -> str:
        """
        Convert Yahoo Finance Thai ticker format to SETSMART format
        
        Examples:
            'PTT.BK' -> 'PTT'
            'ADVANC.BK' -> 'ADVANC'
            'SCB.BK' -> 'SCB'
        """
        if ticker.endswith('.BK'):
            return ticker[:-3]
        return ticker
    
    def _is_thai_stock(self, ticker: str) -> bool:
        """Check if ticker is a Thai stock"""
        return ticker.endswith('.BK')
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make API request with retry logic
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response or None on failure
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        for attempt in range(self._max_retries):
            try:
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # Rate limited, wait and retry
                    wait_time = self._retry_delay * (2 ** attempt)
                    logger.warning(f"SETSMART rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                elif response.status_code == 401:
                    logger.error("SETSMART API key invalid or expired")
                    self._available = False
                    return None
                elif response.status_code == 404:
                    logger.debug(f"SETSMART: Symbol not found for {endpoint}")
                    return None
                else:
                    logger.warning(f"SETSMART API error {response.status_code}: {response.text}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"SETSMART request timeout (attempt {attempt + 1})")
            except requests.exceptions.RequestException as e:
                logger.warning(f"SETSMART request error: {e}")
                
            if attempt < self._max_retries - 1:
                time.sleep(self._retry_delay * (attempt + 1))
        
        return None
    
    def get_price_data(
        self, 
        ticker: str, 
        period: str = "1y",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Get EOD price data for a Thai stock
        
        Args:
            ticker: Stock ticker (e.g., 'PTT.BK' or 'PTT')
            period: Time period ('1y', '6mo', '3mo', '1mo')
            interval: Data interval (only '1d' supported for EOD)
            
        Returns:
            DataFrame with columns: date, open, high, low, close, volume
        """
        if not self._available:
            return None
        
        # Only handle Thai stocks
        if not self._is_thai_stock(ticker) and '.' in ticker:
            return None
        
        symbol = self._convert_ticker(ticker)
        
        # Calculate date range based on period
        end_date = datetime.now()
        if period == "1y":
            start_date = end_date - timedelta(days=365)
        elif period == "6mo":
            start_date = end_date - timedelta(days=180)
        elif period == "3mo":
            start_date = end_date - timedelta(days=90)
        elif period == "1mo":
            start_date = end_date - timedelta(days=30)
        elif period == "2y":
            start_date = end_date - timedelta(days=730)
        elif period == "5y":
            start_date = end_date - timedelta(days=1825)
        else:
            start_date = end_date - timedelta(days=365)
        
        params = {
            "symbol": symbol,
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d")
        }
        
        # Try EOD price endpoint
        data = self._make_request("eod-price-by-symbol", params)
        
        if not data or not isinstance(data, list) or len(data) == 0:
            # Try alternative endpoint format
            data = self._make_request(f"stock/{symbol}/eod", params)
        
        if not data or not isinstance(data, list) or len(data) == 0:
            logger.debug(f"SETSMART: No price data for {symbol}")
            return None
        
        try:
            df = pd.DataFrame(data)
            
            # Standardize column names (SETSMART uses various formats)
            column_mapping = {
                'trade_date': 'date',
                'tradeDate': 'date',
                'date': 'date',
                'open_price': 'open',
                'openPrice': 'open',
                'open': 'open',
                'high_price': 'high',
                'highPrice': 'high',
                'high': 'high',
                'low_price': 'low',
                'lowPrice': 'low',
                'low': 'low',
                'close_price': 'close',
                'closePrice': 'close',
                'close': 'close',
                'last': 'close',
                'volume': 'volume',
                'total_volume': 'volume',
                'totalVolume': 'volume'
            }
            
            df = df.rename(columns=column_mapping)
            
            # Ensure required columns exist
            required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
            missing_cols = [c for c in required_cols if c not in df.columns]
            
            if missing_cols:
                logger.warning(f"SETSMART: Missing columns {missing_cols} for {symbol}")
                # Try to fill missing with close if available
                if 'close' in df.columns:
                    for col in ['open', 'high', 'low']:
                        if col not in df.columns:
                            df[col] = df['close']
                    if 'volume' not in df.columns:
                        df['volume'] = 0
                    if 'date' not in df.columns:
                        return None
                else:
                    return None
            
            # Convert date column
            df['date'] = pd.to_datetime(df['date'])
            
            # Sort by date ascending
            df = df.sort_values('date').reset_index(drop=True)
            
            # Convert numeric columns
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
            
        except Exception as e:
            logger.error(f"SETSMART: Error parsing price data for {symbol}: {e}")
            return None
    
    def get_fundamental_data(self, ticker: str) -> Optional[Dict]:
        """
        Get fundamental data for a Thai stock
        
        Args:
            ticker: Stock ticker (e.g., 'PTT.BK' or 'PTT')
            
        Returns:
            Dict with fundamental metrics
        """
        if not self._available:
            return None
        
        # Only handle Thai stocks
        if not self._is_thai_stock(ticker) and '.' in ticker:
            return None
        
        symbol = self._convert_ticker(ticker)
        
        # Get company fundamental data
        data = self._make_request(f"company/{symbol}/fundamental")
        
        if not data:
            # Try alternative endpoint
            data = self._make_request("company-fundamental", {"symbol": symbol})
        
        if not data:
            logger.debug(f"SETSMART: No fundamental data for {symbol}")
            return None
        
        try:
            # Handle if data is a list (take latest)
            if isinstance(data, list) and len(data) > 0:
                data = data[-1]
            
            # Map SETSMART fields to our standard format
            fundamental = {
                "ticker": ticker,
                "name": data.get("companyName") or data.get("company_name") or data.get("name") or symbol,
                "price": self._safe_float(data.get("lastPrice") or data.get("last_price") or data.get("close")),
                "market_cap": self._safe_float(data.get("marketCap") or data.get("market_cap")),
                
                # Valuation metrics
                "pe_ratio": self._safe_float(data.get("pe") or data.get("peRatio") or data.get("pe_ratio")),
                "forward_pe": self._safe_float(data.get("forwardPe") or data.get("forward_pe")),
                "pb_ratio": self._safe_float(data.get("pb") or data.get("pbRatio") or data.get("pb_ratio") or data.get("priceBook")),
                "ps_ratio": self._safe_float(data.get("ps") or data.get("psRatio") or data.get("ps_ratio")),
                "peg_ratio": self._safe_float(data.get("peg") or data.get("pegRatio")),
                
                # EV metrics
                "enterprise_value": self._safe_float(data.get("enterpriseValue") or data.get("ev")),
                "ev_to_ebitda": self._safe_float(data.get("evEbitda") or data.get("ev_ebitda")),
                
                # Profitability
                "roe": self._safe_float(data.get("roe") or data.get("returnOnEquity")),
                "roa": self._safe_float(data.get("roa") or data.get("returnOnAssets")),
                "profit_margin": self._safe_float(data.get("netProfitMargin") or data.get("profitMargin") or data.get("npm")),
                "operating_margin": self._safe_float(data.get("operatingMargin") or data.get("opm")),
                "gross_margin": self._safe_float(data.get("grossMargin") or data.get("gpm")),
                
                # Growth
                "revenue_growth": self._safe_float(data.get("revenueGrowth") or data.get("revenue_growth")),
                "earnings_growth": self._safe_float(data.get("earningsGrowth") or data.get("earnings_growth") or data.get("epsGrowth")),
                
                # Dividends
                "dividend_yield": self._safe_float(data.get("dividendYield") or data.get("dividend_yield") or data.get("dy")),
                "payout_ratio": self._safe_float(data.get("payoutRatio") or data.get("payout_ratio")),
                
                # Financial health
                "debt_to_equity": self._safe_float(data.get("debtToEquity") or data.get("de") or data.get("debt_equity")),
                "current_ratio": self._safe_float(data.get("currentRatio") or data.get("current_ratio")),
                
                # Per share
                "eps": self._safe_float(data.get("eps") or data.get("earningsPerShare")),
                "book_value": self._safe_float(data.get("bookValue") or data.get("book_value") or data.get("bvps")),
                
                # Other
                "beta": self._safe_float(data.get("beta")),
                "52w_high": self._safe_float(data.get("high52w") or data.get("52w_high") or data.get("yearHigh")),
                "52w_low": self._safe_float(data.get("low52w") or data.get("52w_low") or data.get("yearLow")),
                "avg_volume": self._safe_float(data.get("avgVolume") or data.get("averageVolume")),
            }
            
            # Only return if we have at least price
            if fundamental.get('price') is not None:
                return fundamental
            
            # Try to get price from EOD data
            price_df = self.get_price_data(ticker, period="1mo")
            if price_df is not None and not price_df.empty:
                fundamental['price'] = float(price_df['close'].iloc[-1])
                return fundamental
            
            return None
            
        except Exception as e:
            logger.error(f"SETSMART: Error parsing fundamental data for {symbol}: {e}")
            return None
    
    @staticmethod
    def _safe_float(value) -> Optional[float]:
        """Safely convert value to float"""
        if value is None:
            return None
        try:
            result = float(value)
            # Handle special cases
            if pd.isna(result) or result != result:  # NaN check
                return None
            return result
        except (ValueError, TypeError):
            return None
    
    def get_sector_info(self, ticker: str) -> Optional[Dict]:
        """
        Get SET official sector/industry classification for a stock
        
        Args:
            ticker: Stock ticker (e.g., 'PTT.BK' or 'PTT')
            
        Returns:
            Dict with sector, industry, sub_industry
        """
        if not self._available:
            return None
        
        # Only handle Thai stocks
        if not self._is_thai_stock(ticker) and '.' in ticker:
            return None
        
        symbol = self._convert_ticker(ticker)
        
        # Get company profile with sector info
        data = self._make_request(f"company/{symbol}/profile")
        
        if not data:
            data = self._make_request("company-profile", {"symbol": symbol})
        
        if not data:
            return None
        
        try:
            if isinstance(data, list) and len(data) > 0:
                data = data[0]
            
            return {
                "ticker": ticker,
                "symbol": symbol,
                "name": data.get("companyName") or data.get("company_name") or data.get("name") or symbol,
                "sector": data.get("sector") or data.get("sectorName") or data.get("industry_group"),
                "industry": data.get("industry") or data.get("industryName") or data.get("sub_industry"),
                "sub_industry": data.get("subIndustry") or data.get("sub_industry_name"),
                "market": data.get("market") or "SET",
                "listed_date": data.get("listedDate") or data.get("listed_date"),
                "market_cap": self._safe_float(data.get("marketCap") or data.get("market_cap")),
            }
        except Exception as e:
            logger.error(f"SETSMART: Error parsing sector info for {symbol}: {e}")
            return None
    
    def get_financial_statements(
        self, 
        ticker: str, 
        years: int = 3,
        quarters: int = 12
    ) -> Optional[Dict]:
        """
        Get quarterly financial statements from SETSMART
        
        Args:
            ticker: Stock ticker (e.g., 'PTT.BK' or 'PTT')
            years: Number of years of historical data
            quarters: Number of quarters to fetch
            
        Returns:
            Dict with income_statement, balance_sheet, cash_flow data
        """
        if not self._available:
            return None
        
        # Only handle Thai stocks
        if not self._is_thai_stock(ticker) and '.' in ticker:
            return None
        
        symbol = self._convert_ticker(ticker)
        
        # Calculate date range
        end_year = datetime.now().year
        end_quarter = (datetime.now().month - 1) // 3 + 1
        start_year = end_year - years
        start_quarter = 1
        
        params = {
            "symbol": symbol,
            "startYear": str(start_year),
            "startQuarter": str(start_quarter),
            "endYear": str(end_year),
            "endQuarter": str(end_quarter),
            "statementType": "U"  # Company financial statement
        }
        
        # Try the financial data endpoint
        data = self._make_request("listed-company-api/financial-data-and-ratio-by-symbol", params)
        
        if not data:
            # Try alternative endpoint
            data = self._make_request(f"company/{symbol}/financials", params)
        
        if not data:
            return None
        
        try:
            if isinstance(data, dict):
                data = [data]
            
            if not isinstance(data, list) or len(data) == 0:
                return None
            
            # Parse financial statements
            income_statements = []
            balance_sheets = []
            cash_flows = []
            
            for record in data:
                period = {
                    "year": record.get("fiscalYear") or record.get("year"),
                    "quarter": record.get("fiscalQuarter") or record.get("quarter"),
                    "period_end": record.get("periodEnd") or record.get("period_end_date"),
                }
                
                # Income Statement items
                income = {
                    **period,
                    "revenue": self._safe_float(record.get("totalRevenue") or record.get("revenue") or record.get("sales")),
                    "cost_of_revenue": self._safe_float(record.get("costOfRevenue") or record.get("cost_of_sales")),
                    "gross_profit": self._safe_float(record.get("grossProfit") or record.get("gross_profit")),
                    "operating_income": self._safe_float(record.get("operatingIncome") or record.get("operating_profit") or record.get("ebit")),
                    "ebitda": self._safe_float(record.get("ebitda") or record.get("EBITDA")),
                    "net_income": self._safe_float(record.get("netIncome") or record.get("net_profit") or record.get("profit")),
                    "eps": self._safe_float(record.get("eps") or record.get("earningsPerShare")),
                }
                if any(v is not None for k, v in income.items() if k not in ['year', 'quarter', 'period_end']):
                    income_statements.append(income)
                
                # Balance Sheet items
                balance = {
                    **period,
                    "total_assets": self._safe_float(record.get("totalAssets") or record.get("total_assets")),
                    "total_liabilities": self._safe_float(record.get("totalLiabilities") or record.get("total_liabilities")),
                    "total_equity": self._safe_float(record.get("totalEquity") or record.get("shareholders_equity")),
                    "total_debt": self._safe_float(record.get("totalDebt") or record.get("total_debt")),
                    "cash": self._safe_float(record.get("cash") or record.get("cashAndEquivalents")),
                    "current_assets": self._safe_float(record.get("currentAssets") or record.get("current_assets")),
                    "current_liabilities": self._safe_float(record.get("currentLiabilities") or record.get("current_liabilities")),
                    "book_value_per_share": self._safe_float(record.get("bookValuePerShare") or record.get("bvps")),
                }
                if any(v is not None for k, v in balance.items() if k not in ['year', 'quarter', 'period_end']):
                    balance_sheets.append(balance)
                
                # Cash Flow items
                cash = {
                    **period,
                    "operating_cash_flow": self._safe_float(record.get("operatingCashFlow") or record.get("cfo")),
                    "investing_cash_flow": self._safe_float(record.get("investingCashFlow") or record.get("cfi")),
                    "financing_cash_flow": self._safe_float(record.get("financingCashFlow") or record.get("cff")),
                    "free_cash_flow": self._safe_float(record.get("freeCashFlow") or record.get("fcf")),
                    "capex": self._safe_float(record.get("capitalExpenditures") or record.get("capex")),
                }
                if any(v is not None for k, v in cash.items() if k not in ['year', 'quarter', 'period_end']):
                    cash_flows.append(cash)
            
            # Also include key ratios
            latest = data[-1] if data else {}
            ratios = {
                "pe_ratio": self._safe_float(latest.get("pe") or latest.get("peRatio")),
                "pb_ratio": self._safe_float(latest.get("pb") or latest.get("pbRatio")),
                "roe": self._safe_float(latest.get("roe")),
                "roa": self._safe_float(latest.get("roa")),
                "debt_to_equity": self._safe_float(latest.get("debtToEquity") or latest.get("de")),
                "current_ratio": self._safe_float(latest.get("currentRatio")),
                "gross_margin": self._safe_float(latest.get("grossMargin")),
                "net_margin": self._safe_float(latest.get("netMargin") or latest.get("npm")),
                "dividend_yield": self._safe_float(latest.get("dividendYield") or latest.get("dy")),
            }
            
            return {
                "ticker": ticker,
                "symbol": symbol,
                "income_statement": sorted(income_statements, key=lambda x: (x.get('year') or 0, x.get('quarter') or 0)),
                "balance_sheet": sorted(balance_sheets, key=lambda x: (x.get('year') or 0, x.get('quarter') or 0)),
                "cash_flow": sorted(cash_flows, key=lambda x: (x.get('year') or 0, x.get('quarter') or 0)),
                "ratios": ratios,
                "periods_available": len(income_statements),
            }
            
        except Exception as e:
            logger.error(f"SETSMART: Error parsing financial statements for {symbol}: {e}")
            return None
    
    def get_all_sectors(self) -> Optional[List[Dict]]:
        """
        Get list of all SET sectors with stock counts
        
        Returns:
            List of sectors with name, count, and key metrics
        """
        if not self._available:
            return None
        
        # Try to get sector list from SETSMART
        data = self._make_request("sectors")
        
        if not data:
            data = self._make_request("market/sectors")
        
        if data and isinstance(data, list):
            return [
                {
                    "sector": s.get("sectorName") or s.get("name") or s.get("sector"),
                    "count": s.get("stockCount") or s.get("count") or 0,
                    "market_cap": self._safe_float(s.get("marketCap")),
                    "pe_avg": self._safe_float(s.get("peAvg") or s.get("avgPe")),
                    "change_pct": self._safe_float(s.get("changePct") or s.get("change")),
                }
                for s in data
            ]
        
        # Fallback: Return SET official sectors
        return [
            {"sector": "Resources", "count": 0},
            {"sector": "Technology", "count": 0},
            {"sector": "Industrials", "count": 0},
            {"sector": "Property & Construction", "count": 0},
            {"sector": "Financials", "count": 0},
            {"sector": "Services", "count": 0},
            {"sector": "Consumer Products", "count": 0},
            {"sector": "Agro & Food Industry", "count": 0},
        ]
