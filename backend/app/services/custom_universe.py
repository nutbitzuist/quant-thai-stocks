"""
Custom Universe Manager
Allows users to create and manage their own stock universes
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
import re


@dataclass
class CustomUniverse:
    """A user-defined stock universe"""
    id: str
    name: str
    description: str
    tickers: List[str]
    market: str  # "US", "Thailand", "Mixed"
    created_at: str
    updated_at: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


class CustomUniverseManager:
    """
    Manages custom user-defined universes
    """
    
    def __init__(self):
        self._universes: Dict[str, CustomUniverse] = {}
        self._load_examples()
    
    def _load_examples(self):
        """Load some example custom universes"""
        # Example: FAANG stocks
        self.create_universe(
            name="FAANG",
            description="Facebook (Meta), Apple, Amazon, Netflix, Google",
            tickers=["META", "AAPL", "AMZN", "NFLX", "GOOGL"],
            market="US"
        )
        
        # Example: Thai Banks
        self.create_universe(
            name="Thai Banks",
            description="Major Thai commercial banks",
            tickers=["KBANK.BK", "BBL.BK", "SCB.BK", "KTB.BK", "TTB.BK", "TISCO.BK"],
            market="Thailand"
        )
        
        # Example: Magnificent 7
        self.create_universe(
            name="Magnificent 7",
            description="The 7 largest US tech companies by market cap",
            tickers=["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"],
            market="US"
        )
    
    def _generate_id(self, name: str) -> str:
        """Generate a unique ID from name"""
        # Convert to lowercase, replace spaces with underscores
        base_id = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
        
        # Ensure uniqueness
        if base_id not in self._universes:
            return base_id
        
        counter = 1
        while f"{base_id}_{counter}" in self._universes:
            counter += 1
        return f"{base_id}_{counter}"
    
    def _normalize_ticker(self, ticker: str) -> str:
        """Normalize ticker format"""
        ticker = ticker.strip().upper()
        # Remove common suffixes that might be incorrectly added
        if ticker.endswith('.US'):
            ticker = ticker[:-3]
        return ticker
    
    def create_universe(
        self,
        name: str,
        description: str,
        tickers: List[str],
        market: str = "Mixed"
    ) -> CustomUniverse:
        """Create a new custom universe"""
        universe_id = self._generate_id(name)
        now = datetime.now().isoformat()
        
        # Normalize tickers
        normalized_tickers = [self._normalize_ticker(t) for t in tickers if t.strip()]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tickers = []
        for t in normalized_tickers:
            if t not in seen:
                seen.add(t)
                unique_tickers.append(t)
        
        universe = CustomUniverse(
            id=universe_id,
            name=name,
            description=description,
            tickers=unique_tickers,
            market=market,
            created_at=now,
            updated_at=now
        )
        
        self._universes[universe_id] = universe
        return universe
    
    def update_universe(
        self,
        universe_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tickers: Optional[List[str]] = None,
        market: Optional[str] = None
    ) -> Optional[CustomUniverse]:
        """Update an existing custom universe"""
        if universe_id not in self._universes:
            return None
        
        universe = self._universes[universe_id]
        
        if name is not None:
            universe.name = name
        if description is not None:
            universe.description = description
        if tickers is not None:
            normalized = [self._normalize_ticker(t) for t in tickers if t.strip()]
            seen = set()
            unique_tickers = []
            for t in normalized:
                if t not in seen:
                    seen.add(t)
                    unique_tickers.append(t)
            universe.tickers = unique_tickers
        if market is not None:
            universe.market = market
        
        universe.updated_at = datetime.now().isoformat()
        return universe
    
    def delete_universe(self, universe_id: str) -> bool:
        """Delete a custom universe"""
        if universe_id in self._universes:
            del self._universes[universe_id]
            return True
        return False
    
    def get_universe(self, universe_id: str) -> Optional[CustomUniverse]:
        """Get a specific custom universe"""
        return self._universes.get(universe_id)
    
    def get_all_universes(self) -> List[Dict]:
        """Get all custom universes"""
        return [
            {
                "id": u.id,
                "name": u.name,
                "description": u.description,
                "market": u.market,
                "count": len(u.tickers),
                "created_at": u.created_at
            }
            for u in self._universes.values()
        ]
    
    def get_tickers(self, universe_id: str) -> List[str]:
        """Get tickers for a custom universe"""
        universe = self._universes.get(universe_id)
        return universe.tickers if universe else []
    
    def parse_ticker_input(self, input_text: str) -> List[str]:
        """
        Parse ticker input from user (flexible format)
        Accepts: comma-separated, space-separated, newline-separated, or mixed
        """
        # Replace various delimiters with comma
        normalized = input_text.replace('\n', ',').replace('\t', ',').replace(';', ',')
        
        # Split and clean
        tickers = []
        for part in normalized.split(','):
            # Also split by spaces
            for ticker in part.split():
                cleaned = ticker.strip().upper()
                if cleaned and len(cleaned) <= 10:  # Basic validation
                    tickers.append(cleaned)
        
        return tickers
    
    def import_from_text(
        self,
        name: str,
        description: str,
        ticker_text: str,
        market: str = "Mixed"
    ) -> CustomUniverse:
        """Create universe from text input (flexible format)"""
        tickers = self.parse_ticker_input(ticker_text)
        return self.create_universe(name, description, tickers, market)


# Singleton instance
_custom_universe_manager = None

def get_custom_universe_manager() -> CustomUniverseManager:
    global _custom_universe_manager
    if _custom_universe_manager is None:
        _custom_universe_manager = CustomUniverseManager()
    return _custom_universe_manager
