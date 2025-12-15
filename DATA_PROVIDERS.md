# Data Providers Guide

## Overview

The system now supports **multiple data providers** simultaneously, with automatic fallback capabilities. This improves data quality, reliability, and redundancy.

## Current Libraries

### Primary (Always Installed)
- **yfinance** (v0.2.36+) - Yahoo Finance data (default, most reliable)

### Optional (Install as Needed)
- **pandas-datareader** - Alternative data sources (Yahoo, Stooq, FRED, etc.)
- **alpha-vantage** - Alpha Vantage API (requires API key)
- **yahooquery** - Alternative Yahoo Finance library
- **investpy** - Investing.com data (good for international/Thai stocks)
- **quandl** - Nasdaq Data Link (requires API key)

## How It Works

### Multiple Providers at Once
✅ **YES, you can use multiple libraries simultaneously!**

The system:
1. Tries providers in order (yfinance first by default)
2. Falls back to the next provider if one fails
3. Caches successful results
4. Logs errors for debugging

### Configuration

#### Environment Variables

```bash
# Specify which providers to use (comma-separated, in order)
DATA_PROVIDERS=yfinance,pandas_datareader_yahoo,alpha_vantage

# Enable/disable automatic fallback
DATA_FALLBACK_ENABLED=true

# Alpha Vantage API key (if using alpha_vantage)
ALPHA_VANTAGE_API_KEY=your_key_here
```

#### Default Behavior
- If `DATA_PROVIDERS` is not set, uses **all available providers**
- Providers are tried in order: yfinance → pandas_datareader → alpha_vantage
- Fallback is **enabled by default**

## Installation

### Install Optional Providers

```bash
# Install all optional providers
pip install pandas-datareader alpha-vantage yahooquery investpy quandl

# Or install specific ones
pip install pandas-datareader  # For alternative Yahoo/Stooq data
pip install alpha-vantage      # For Alpha Vantage API
pip install investpy           # Good for Thai/international stocks
```

### Update requirements.txt

Uncomment the providers you want in `backend/requirements.txt`:

```txt
# Optional Data Providers
pandas-datareader>=0.10.0
alpha-vantage>=2.3.1
yahooquery>=2.3.1
investpy>=1.0.9
quandl>=3.7.0
```

## Usage Examples

### Check Available Providers

```bash
# API endpoint
GET /api/status/data-providers

# Response:
{
  "active_providers": ["yfinance", "pandas_datareader_yahoo"],
  "fallback_enabled": true,
  "all_available_providers": [
    {"name": "yfinance", "available": true},
    {"name": "pandas_datareader_yahoo", "available": true},
    {"name": "alpha_vantage", "available": false}
  ]
}
```

### System Status

```bash
GET /api/status/

# Shows active providers and cache status
```

## Benefits

### 1. **Improved Data Quality**
- Cross-validate data from multiple sources
- Fill gaps when one provider has missing data

### 2. **Better Reliability**
- Automatic fallback if one provider is down
- Redundancy reduces single points of failure

### 3. **Market Coverage**
- Different providers excel at different markets
- investpy is better for Thai stocks
- yfinance is best for US stocks

### 4. **Rate Limiting Protection**
- Distribute requests across providers
- Avoid hitting rate limits on single provider

## Provider Details

### yfinance (Default)
- **Best for**: US stocks, major international stocks
- **Coverage**: Price data, fundamentals, options
- **Rate Limits**: Moderate
- **Cost**: Free
- **Installation**: Already included

### pandas-datareader
- **Best for**: Historical data, alternative sources
- **Coverage**: Multiple backends (Yahoo, Stooq, FRED)
- **Rate Limits**: Varies by backend
- **Cost**: Free
- **Installation**: `pip install pandas-datareader`

### alpha-vantage
- **Best for**: Real-time data, technical indicators
- **Coverage**: Price, fundamentals, technicals
- **Rate Limits**: 5 calls/min (free), 75/min (premium)
- **Cost**: Free tier available, paid plans available
- **Installation**: `pip install alpha-vantage`
- **Setup**: Requires `ALPHA_VANTAGE_API_KEY` environment variable

### investpy
- **Best for**: International stocks, including Thai stocks
- **Coverage**: Price data for many international markets
- **Rate Limits**: Moderate
- **Cost**: Free
- **Installation**: `pip install investpy`

### setsmart ⭐ (Recommended for Thai Stocks)
- **Best for**: Thai stocks (SET50, SET100) - Official SET data
- **Coverage**: EOD prices, fundamentals, P/E, P/B, ROE, dividend yields
- **Rate Limits**: Depends on subscription tier
- **Cost**: Requires SETSMART subscription
- **Setup**: Requires `SETSMART_API_KEY` environment variable
- **Get API key**: Login to [setsmart.com](https://www.setsmart.com) → Tools → API Service
- **Data quality**: Direct from Stock Exchange of Thailand - most accurate for Thai stocks

## Best Practices

### For Thai Stocks ⭐ (Recommended)
```bash
# Best setup with SETSMART API (official SET data)
SETSMART_API_KEY=your_setsmart_api_key
DATA_PROVIDERS=setsmart,yfinance
```

### For US Stocks
```bash
# Recommended setup (default)
DATA_PROVIDERS=yfinance,pandas_datareader_yahoo
```

### For Maximum Reliability
```bash
# Use all available providers
DATA_PROVIDERS=setsmart,yfinance,pandas_datareader_yahoo,alpha_vantage
DATA_FALLBACK_ENABLED=true
```

### For Specific Provider Only
```bash
# Use only yfinance (no fallback)
DATA_PROVIDERS=yfinance
DATA_FALLBACK_ENABLED=false
```

## Troubleshooting

### Provider Not Available
- Check if the library is installed: `pip list | grep <library>`
- Check provider status: `GET /api/status/data-providers`
- Review logs for import errors

### API Key Issues
- **SETSMART**: Set `SETSMART_API_KEY` environment variable
  - Get API key at: [setsmart.com](https://www.setsmart.com) → Tools → API Service
- **Alpha Vantage**: Set `ALPHA_VANTAGE_API_KEY` environment variable
  - Get free API key at: https://www.alphavantage.co/support/#api-key

### Data Quality Issues
- Enable multiple providers for cross-validation
- Check error logs: `GET /api/status/logs`
- Try different provider order in `DATA_PROVIDERS`

## Architecture

```
DataFetcher
    ├── Provider 1 (setsmart)         → Best for Thai stocks (if API key set)
    ├── Provider 2 (yfinance)         → Default, best for US stocks
    ├── Provider 3 (pandas_datareader) → Fallback
    └── Provider 4 (alpha_vantage)     → Fallback (if API key set)
```

Each provider implements the `DataProvider` interface:
- `get_price_data()` - Fetch price/OHLCV data
- `get_fundamental_data()` - Fetch financial metrics
- `is_available()` - Check if provider is configured
- `get_name()` - Get provider identifier

## Adding New Providers

To add a new data provider:

1. Create a new class in `backend/app/data/providers.py`
2. Inherit from `DataProvider` base class
3. Implement required methods
4. Add to `get_available_providers()` function
5. Update `requirements.txt` with the library

Example:
```python
class MyNewProvider(DataProvider):
    def get_name(self) -> str:
        return "my_new_provider"
    
    def is_available(self) -> bool:
        # Check if library is installed
        try:
            import my_library
            return True
        except ImportError:
            return False
    
    def get_price_data(self, ticker, period, interval):
        # Implement data fetching
        pass
    
    def get_fundamental_data(self, ticker):
        # Implement fundamental data fetching
        pass
```

## Summary

✅ **Multiple libraries can be used simultaneously**
✅ **Automatic fallback improves reliability**
✅ **Easy configuration via environment variables**
✅ **Extensible architecture for adding new providers**

The system is designed to be flexible and robust, allowing you to use the best data sources for your specific needs!

