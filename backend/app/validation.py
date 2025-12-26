"""
Input Validation Utilities
Validates and sanitizes user input to prevent injection attacks
"""

import re
from typing import List, Optional, Any
from fastapi import HTTPException, Query, Path
from pydantic import validator

# Regex patterns
TICKER_PATTERN = re.compile(r'^[A-Z0-9\.\-]{1,20}$')
NAME_PATTERN = re.compile(r'^[\w\s\-\.\'\"]+$', re.UNICODE)
TIME_PATTERN = re.compile(r'^([01]\d|2[0-3]):([0-5]\d)$')

# Valid day names
VALID_DAYS = {'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'}

# Limits
MAX_NAME_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 500
MAX_TICKERS_PER_UNIVERSE = 500
MAX_TOP_N = 100
MAX_LIMIT = 100
MAX_SIMULATIONS = 10000


def validate_ticker(ticker: str) -> str:
    """
    Validate and normalize a stock ticker symbol.
    
    Args:
        ticker: The ticker string to validate
        
    Returns:
        Normalized ticker (uppercase, trimmed)
        
    Raises:
        HTTPException: If ticker format is invalid
    """
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker cannot be empty")
    
    ticker = ticker.strip().upper()
    
    if len(ticker) > 20:
        raise HTTPException(
            status_code=400, 
            detail="Ticker too long (max 20 characters)"
        )
    
    if not TICKER_PATTERN.match(ticker):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid ticker format: {ticker}. Use letters, numbers, dots, or hyphens only."
        )
    
    return ticker


def validate_ticker_path(ticker: str = Path(..., description="Stock ticker symbol")) -> str:
    """Validate ticker from path parameter"""
    return validate_ticker(ticker)


def validate_name(name: str, field_name: str = "Name") -> str:
    """
    Validate and sanitize a name field (universe name, scan name, etc.)
    
    Args:
        name: The name to validate
        field_name: Field name for error messages
        
    Returns:
        Sanitized name
        
    Raises:
        HTTPException: If name is invalid
    """
    if not name:
        raise HTTPException(status_code=400, detail=f"{field_name} cannot be empty")
    
    name = name.strip()
    
    if len(name) > MAX_NAME_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} too long (max {MAX_NAME_LENGTH} characters)"
        )
    
    if len(name) < 1:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} cannot be empty"
        )
    
    # Allow alphanumeric, spaces, hyphens, dots, quotes
    if not NAME_PATTERN.match(name):
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} contains invalid characters"
        )
    
    return name


def validate_description(description: Optional[str], field_name: str = "Description") -> Optional[str]:
    """
    Validate and sanitize a description field.
    
    Args:
        description: The description to validate (can be None)
        field_name: Field name for error messages
        
    Returns:
        Sanitized description or None
    """
    if not description:
        return None
    
    description = description.strip()
    
    if len(description) > MAX_DESCRIPTION_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} too long (max {MAX_DESCRIPTION_LENGTH} characters)"
        )
    
    # Basic HTML tag removal for security
    description = re.sub(r'<[^>]+>', '', description)
    
    return description


def validate_schedule_time(time_str: str) -> str:
    """
    Validate schedule time format (HH:MM).
    
    Args:
        time_str: Time string to validate
        
    Returns:
        Validated time string
        
    Raises:
        HTTPException: If format is invalid
    """
    if not time_str:
        raise HTTPException(status_code=400, detail="Schedule time cannot be empty")
    
    time_str = time_str.strip()
    
    if not TIME_PATTERN.match(time_str):
        raise HTTPException(
            status_code=400,
            detail="Invalid time format. Use HH:MM (e.g., 09:30)"
        )
    
    return time_str


def validate_days(days: List[str]) -> List[str]:
    """
    Validate day names for scheduling.
    
    Args:
        days: List of day abbreviations
        
    Returns:
        Validated list of days
        
    Raises:
        HTTPException: If any day is invalid
    """
    if not days:
        raise HTTPException(status_code=400, detail="At least one day must be selected")
    
    invalid_days = [d for d in days if d not in VALID_DAYS]
    
    if invalid_days:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid day names: {invalid_days}. Valid values: {list(VALID_DAYS)}"
        )
    
    return days


def validate_ticker_list(tickers: List[str]) -> List[str]:
    """
    Validate a list of tickers.
    
    Args:
        tickers: List of ticker strings
        
    Returns:
        List of validated, normalized tickers
        
    Raises:
        HTTPException: If any ticker is invalid or list is too long
    """
    if not tickers:
        raise HTTPException(status_code=400, detail="Ticker list cannot be empty")
    
    if len(tickers) > MAX_TICKERS_PER_UNIVERSE:
        raise HTTPException(
            status_code=400,
            detail=f"Too many tickers (max {MAX_TICKERS_PER_UNIVERSE})"
        )
    
    validated = []
    for ticker in tickers:
        validated.append(validate_ticker(ticker))
    
    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for t in validated:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    
    return unique


def validate_limit(
    limit: int = Query(50, description="Maximum records to return", ge=1, le=MAX_LIMIT)
) -> int:
    """Validate limit parameter"""
    return min(limit, MAX_LIMIT)


def validate_top_n(
    top_n: int = Query(10, description="Number of top results", ge=1, le=MAX_TOP_N)
) -> int:
    """Validate top_n parameter"""
    return min(top_n, MAX_TOP_N)


def validate_n_simulations(
    n_simulations: int = Query(1000, description="Number of simulations", ge=1, le=MAX_SIMULATIONS)
) -> int:
    """Validate n_simulations parameter for Monte Carlo"""
    return min(n_simulations, MAX_SIMULATIONS)


def sanitize_error_message(error: Exception) -> str:
    """
    Sanitize an error message for client response.
    Removes sensitive information like file paths, stack traces.
    
    Args:
        error: The exception
        
    Returns:
        Sanitized error message
    """
    message = str(error)
    
    # Remove file paths
    message = re.sub(r'/[^\s]+\.py', '[file]', message)
    message = re.sub(r'line \d+', '[line]', message)
    
    # Truncate if too long
    if len(message) > 200:
        message = message[:200] + "..."
    
    return message
