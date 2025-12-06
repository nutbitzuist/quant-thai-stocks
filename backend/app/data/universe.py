"""
Stock Universe Definitions
Supports multiple markets: SET (Thailand), S&P 500 (US)
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional


class Market(Enum):
    THAILAND = "SET"
    US = "US"


class Sector(Enum):
    TECHNOLOGY = "Technology"
    HEALTHCARE = "Healthcare"
    FINANCIALS = "Financials"
    ENERGY = "Energy"
    CONSUMER = "Consumer"
    INDUSTRIALS = "Industrials"
    MATERIALS = "Materials"
    UTILITIES = "Utilities"
    REAL_ESTATE = "Real Estate"
    COMMUNICATIONS = "Communications"
    OTHER = "Other"


@dataclass
class Stock:
    ticker: str
    name: str
    sector: Sector
    market: Market
    is_major: bool = False  # Top 50 in each market


# ============================================================
# S&P 500 - TOP 100 (Most liquid, reliable data)
# ============================================================
SP500_STOCKS: List[Stock] = [
    # === TECHNOLOGY ===
    Stock("AAPL", "Apple Inc", Sector.TECHNOLOGY, Market.US, True),
    Stock("MSFT", "Microsoft", Sector.TECHNOLOGY, Market.US, True),
    Stock("GOOGL", "Alphabet (Google)", Sector.TECHNOLOGY, Market.US, True),
    Stock("AMZN", "Amazon", Sector.TECHNOLOGY, Market.US, True),
    Stock("NVDA", "NVIDIA", Sector.TECHNOLOGY, Market.US, True),
    Stock("META", "Meta Platforms", Sector.TECHNOLOGY, Market.US, True),
    Stock("TSLA", "Tesla", Sector.TECHNOLOGY, Market.US, True),
    Stock("AVGO", "Broadcom", Sector.TECHNOLOGY, Market.US, True),
    Stock("ORCL", "Oracle", Sector.TECHNOLOGY, Market.US, True),
    Stock("CRM", "Salesforce", Sector.TECHNOLOGY, Market.US, True),
    Stock("AMD", "AMD", Sector.TECHNOLOGY, Market.US, True),
    Stock("ADBE", "Adobe", Sector.TECHNOLOGY, Market.US, True),
    Stock("CSCO", "Cisco", Sector.TECHNOLOGY, Market.US, True),
    Stock("ACN", "Accenture", Sector.TECHNOLOGY, Market.US, True),
    Stock("INTC", "Intel", Sector.TECHNOLOGY, Market.US, False),
    Stock("IBM", "IBM", Sector.TECHNOLOGY, Market.US, False),
    Stock("QCOM", "Qualcomm", Sector.TECHNOLOGY, Market.US, False),
    Stock("TXN", "Texas Instruments", Sector.TECHNOLOGY, Market.US, False),
    Stock("NOW", "ServiceNow", Sector.TECHNOLOGY, Market.US, False),
    Stock("INTU", "Intuit", Sector.TECHNOLOGY, Market.US, False),
    
    # === HEALTHCARE ===
    Stock("UNH", "UnitedHealth", Sector.HEALTHCARE, Market.US, True),
    Stock("JNJ", "Johnson & Johnson", Sector.HEALTHCARE, Market.US, True),
    Stock("LLY", "Eli Lilly", Sector.HEALTHCARE, Market.US, True),
    Stock("PFE", "Pfizer", Sector.HEALTHCARE, Market.US, True),
    Stock("ABBV", "AbbVie", Sector.HEALTHCARE, Market.US, True),
    Stock("MRK", "Merck", Sector.HEALTHCARE, Market.US, True),
    Stock("TMO", "Thermo Fisher", Sector.HEALTHCARE, Market.US, True),
    Stock("ABT", "Abbott Labs", Sector.HEALTHCARE, Market.US, True),
    Stock("DHR", "Danaher", Sector.HEALTHCARE, Market.US, False),
    Stock("BMY", "Bristol-Myers", Sector.HEALTHCARE, Market.US, False),
    
    # === FINANCIALS ===
    Stock("BRK-B", "Berkshire Hathaway", Sector.FINANCIALS, Market.US, True),
    Stock("JPM", "JPMorgan Chase", Sector.FINANCIALS, Market.US, True),
    Stock("V", "Visa", Sector.FINANCIALS, Market.US, True),
    Stock("MA", "Mastercard", Sector.FINANCIALS, Market.US, True),
    Stock("BAC", "Bank of America", Sector.FINANCIALS, Market.US, True),
    Stock("WFC", "Wells Fargo", Sector.FINANCIALS, Market.US, True),
    Stock("GS", "Goldman Sachs", Sector.FINANCIALS, Market.US, True),
    Stock("MS", "Morgan Stanley", Sector.FINANCIALS, Market.US, False),
    Stock("BLK", "BlackRock", Sector.FINANCIALS, Market.US, False),
    Stock("C", "Citigroup", Sector.FINANCIALS, Market.US, False),
    
    # === CONSUMER ===
    Stock("WMT", "Walmart", Sector.CONSUMER, Market.US, True),
    Stock("PG", "Procter & Gamble", Sector.CONSUMER, Market.US, True),
    Stock("KO", "Coca-Cola", Sector.CONSUMER, Market.US, True),
    Stock("PEP", "PepsiCo", Sector.CONSUMER, Market.US, True),
    Stock("COST", "Costco", Sector.CONSUMER, Market.US, True),
    Stock("HD", "Home Depot", Sector.CONSUMER, Market.US, True),
    Stock("MCD", "McDonald's", Sector.CONSUMER, Market.US, True),
    Stock("NKE", "Nike", Sector.CONSUMER, Market.US, True),
    Stock("SBUX", "Starbucks", Sector.CONSUMER, Market.US, False),
    Stock("TGT", "Target", Sector.CONSUMER, Market.US, False),
    
    # === INDUSTRIALS ===
    Stock("CAT", "Caterpillar", Sector.INDUSTRIALS, Market.US, True),
    Stock("GE", "General Electric", Sector.INDUSTRIALS, Market.US, True),
    Stock("HON", "Honeywell", Sector.INDUSTRIALS, Market.US, True),
    Stock("UPS", "UPS", Sector.INDUSTRIALS, Market.US, True),
    Stock("RTX", "RTX Corp", Sector.INDUSTRIALS, Market.US, True),
    Stock("BA", "Boeing", Sector.INDUSTRIALS, Market.US, True),
    Stock("LMT", "Lockheed Martin", Sector.INDUSTRIALS, Market.US, False),
    Stock("DE", "Deere & Co", Sector.INDUSTRIALS, Market.US, False),
    Stock("UNP", "Union Pacific", Sector.INDUSTRIALS, Market.US, False),
    Stock("MMM", "3M", Sector.INDUSTRIALS, Market.US, False),
    
    # === ENERGY ===
    Stock("XOM", "Exxon Mobil", Sector.ENERGY, Market.US, True),
    Stock("CVX", "Chevron", Sector.ENERGY, Market.US, True),
    Stock("COP", "ConocoPhillips", Sector.ENERGY, Market.US, False),
    Stock("SLB", "Schlumberger", Sector.ENERGY, Market.US, False),
    Stock("EOG", "EOG Resources", Sector.ENERGY, Market.US, False),
    
    # === COMMUNICATIONS ===
    Stock("NFLX", "Netflix", Sector.COMMUNICATIONS, Market.US, True),
    Stock("DIS", "Disney", Sector.COMMUNICATIONS, Market.US, True),
    Stock("CMCSA", "Comcast", Sector.COMMUNICATIONS, Market.US, False),
    Stock("VZ", "Verizon", Sector.COMMUNICATIONS, Market.US, False),
    Stock("T", "AT&T", Sector.COMMUNICATIONS, Market.US, False),
    
    # === UTILITIES ===
    Stock("NEE", "NextEra Energy", Sector.UTILITIES, Market.US, True),
    Stock("DUK", "Duke Energy", Sector.UTILITIES, Market.US, False),
    Stock("SO", "Southern Co", Sector.UTILITIES, Market.US, False),
    
    # === REAL ESTATE ===
    Stock("AMT", "American Tower", Sector.REAL_ESTATE, Market.US, False),
    Stock("PLD", "Prologis", Sector.REAL_ESTATE, Market.US, False),
    Stock("CCI", "Crown Castle", Sector.REAL_ESTATE, Market.US, False),
    
    # === MATERIALS ===
    Stock("LIN", "Linde", Sector.MATERIALS, Market.US, True),
    Stock("APD", "Air Products", Sector.MATERIALS, Market.US, False),
    Stock("SHW", "Sherwin-Williams", Sector.MATERIALS, Market.US, False),
]


# ============================================================
# SET100 - Thailand (Official list)
# ============================================================
SET100_STOCKS: List[Stock] = [
    # Based on official SET100 constituents
    Stock("AAV.BK", "Asia Aviation", Sector.INDUSTRIALS, Market.THAILAND, False),
    Stock("ADVANC.BK", "Advanced Info Service", Sector.COMMUNICATIONS, Market.THAILAND, True),
    Stock("AEONTS.BK", "AEON Thana Sinsap", Sector.FINANCIALS, Market.THAILAND, False),
    Stock("AMATA.BK", "Amata Corporation", Sector.REAL_ESTATE, Market.THAILAND, False),
    Stock("AOT.BK", "Airports of Thailand", Sector.INDUSTRIALS, Market.THAILAND, True),
    Stock("AP.BK", "AP Thailand", Sector.REAL_ESTATE, Market.THAILAND, False),
    Stock("AWC.BK", "Asset World Corp", Sector.REAL_ESTATE, Market.THAILAND, True),
    Stock("BA.BK", "Bangkok Airways", Sector.INDUSTRIALS, Market.THAILAND, False),
    Stock("BAM.BK", "Bangkok Commercial Asset", Sector.FINANCIALS, Market.THAILAND, False),
    Stock("BANPU.BK", "Banpu", Sector.ENERGY, Market.THAILAND, True),
    Stock("BBL.BK", "Bangkok Bank", Sector.FINANCIALS, Market.THAILAND, True),
    Stock("BCH.BK", "Bangkok Chain Hospital", Sector.HEALTHCARE, Market.THAILAND, False),
    Stock("BCP.BK", "Bangchak Corp", Sector.ENERGY, Market.THAILAND, False),
    Stock("BCPG.BK", "BCPG", Sector.UTILITIES, Market.THAILAND, False),
    Stock("BDMS.BK", "Bangkok Dusit Medical", Sector.HEALTHCARE, Market.THAILAND, True),
    Stock("BEM.BK", "Bangkok Expressway", Sector.INDUSTRIALS, Market.THAILAND, True),
    Stock("BGRIM.BK", "B.Grimm Power", Sector.UTILITIES, Market.THAILAND, True),
    Stock("BH.BK", "Bumrungrad Hospital", Sector.HEALTHCARE, Market.THAILAND, True),
    Stock("BJC.BK", "Berli Jucker", Sector.CONSUMER, Market.THAILAND, True),
    Stock("BLA.BK", "Bangkok Life Assurance", Sector.FINANCIALS, Market.THAILAND, False),
    Stock("BTG.BK", "Betagro", Sector.CONSUMER, Market.THAILAND, False),
    Stock("BTS.BK", "BTS Group", Sector.INDUSTRIALS, Market.THAILAND, True),
    Stock("CBG.BK", "Carabao Group", Sector.CONSUMER, Market.THAILAND, True),
    Stock("CCET.BK", "Cal-Comp Electronics", Sector.TECHNOLOGY, Market.THAILAND, True),
    Stock("CENTEL.BK", "Central Plaza Hotel", Sector.CONSUMER, Market.THAILAND, False),
    Stock("CHG.BK", "Chularat Hospital", Sector.HEALTHCARE, Market.THAILAND, False),
    Stock("CK.BK", "CH Karnchang", Sector.INDUSTRIALS, Market.THAILAND, False),
    Stock("CKP.BK", "CK Power", Sector.UTILITIES, Market.THAILAND, False),
    Stock("COM7.BK", "Com7", Sector.CONSUMER, Market.THAILAND, True),
    Stock("CPALL.BK", "CP All", Sector.CONSUMER, Market.THAILAND, True),
    Stock("CPF.BK", "CP Foods", Sector.CONSUMER, Market.THAILAND, True),
    Stock("CPN.BK", "Central Pattana", Sector.REAL_ESTATE, Market.THAILAND, True),
    Stock("CRC.BK", "Central Retail", Sector.CONSUMER, Market.THAILAND, True),
    Stock("DELTA.BK", "Delta Electronics", Sector.TECHNOLOGY, Market.THAILAND, True),
    Stock("DOHOME.BK", "Dohome", Sector.CONSUMER, Market.THAILAND, False),
    Stock("EA.BK", "Energy Absolute", Sector.UTILITIES, Market.THAILAND, False),
    Stock("EGCO.BK", "Electricity Generating", Sector.UTILITIES, Market.THAILAND, True),
    Stock("ERW.BK", "Erawan Group", Sector.CONSUMER, Market.THAILAND, False),
    Stock("GLOBAL.BK", "Siam Global House", Sector.CONSUMER, Market.THAILAND, True),
    Stock("GPSC.BK", "Global Power Synergy", Sector.UTILITIES, Market.THAILAND, True),
    Stock("GULF.BK", "Gulf Energy", Sector.UTILITIES, Market.THAILAND, True),
    Stock("GUNKUL.BK", "Gunkul Engineering", Sector.UTILITIES, Market.THAILAND, False),
    Stock("HANA.BK", "Hana Microelectronics", Sector.TECHNOLOGY, Market.THAILAND, False),
    Stock("HMPRO.BK", "Home Product Center", Sector.CONSUMER, Market.THAILAND, True),
    Stock("ICHI.BK", "Ichitan Group", Sector.CONSUMER, Market.THAILAND, False),
    Stock("IRPC.BK", "IRPC", Sector.ENERGY, Market.THAILAND, False),
    Stock("ITC.BK", "ITC", Sector.INDUSTRIALS, Market.THAILAND, True),
    Stock("IVL.BK", "Indorama Ventures", Sector.MATERIALS, Market.THAILAND, True),
    Stock("JAS.BK", "Jasmine International", Sector.COMMUNICATIONS, Market.THAILAND, False),
    Stock("JMART.BK", "Jay Mart", Sector.CONSUMER, Market.THAILAND, False),
    Stock("JMT.BK", "JMT Network Services", Sector.FINANCIALS, Market.THAILAND, False),
    Stock("JTS.BK", "Jasmine Technology", Sector.COMMUNICATIONS, Market.THAILAND, False),
    Stock("KBANK.BK", "Kasikornbank", Sector.FINANCIALS, Market.THAILAND, True),
    Stock("KCE.BK", "KCE Electronics", Sector.TECHNOLOGY, Market.THAILAND, False),
    Stock("KKP.BK", "Kiatnakin Phatra", Sector.FINANCIALS, Market.THAILAND, False),
    Stock("KTB.BK", "Krung Thai Bank", Sector.FINANCIALS, Market.THAILAND, True),
    Stock("KTC.BK", "Krungthai Card", Sector.FINANCIALS, Market.THAILAND, True),
    Stock("LH.BK", "Land and Houses", Sector.REAL_ESTATE, Market.THAILAND, True),
    Stock("M.BK", "MK Restaurant", Sector.CONSUMER, Market.THAILAND, False),
    Stock("MEGA.BK", "Mega Lifesciences", Sector.HEALTHCARE, Market.THAILAND, False),
    Stock("MINT.BK", "Minor International", Sector.CONSUMER, Market.THAILAND, True),
    Stock("MTC.BK", "Muangthai Capital", Sector.FINANCIALS, Market.THAILAND, True),
    Stock("OR.BK", "PTT Oil and Retail", Sector.ENERGY, Market.THAILAND, True),
    Stock("OSP.BK", "Osotspa", Sector.CONSUMER, Market.THAILAND, True),
    Stock("PLANB.BK", "Plan B Media", Sector.COMMUNICATIONS, Market.THAILAND, False),
    Stock("PR9.BK", "Praram 9 Hospital", Sector.HEALTHCARE, Market.THAILAND, False),
    Stock("PRM.BK", "Prima Marine", Sector.INDUSTRIALS, Market.THAILAND, False),
    Stock("PTT.BK", "PTT PCL", Sector.ENERGY, Market.THAILAND, True),
    Stock("PTTEP.BK", "PTT Exploration", Sector.ENERGY, Market.THAILAND, True),
    Stock("PTTGC.BK", "PTT Global Chemical", Sector.ENERGY, Market.THAILAND, True),
    Stock("QH.BK", "Quality Houses", Sector.REAL_ESTATE, Market.THAILAND, False),
    Stock("RATCH.BK", "Ratchaburi Electricity", Sector.UTILITIES, Market.THAILAND, True),
    Stock("RCL.BK", "Regional Container Lines", Sector.INDUSTRIALS, Market.THAILAND, False),
    Stock("SAWAD.BK", "Srisawad Corp", Sector.FINANCIALS, Market.THAILAND, True),
    Stock("SCB.BK", "SCB X PCL", Sector.FINANCIALS, Market.THAILAND, True),
    Stock("SCC.BK", "Siam Cement", Sector.MATERIALS, Market.THAILAND, True),
    Stock("SCGP.BK", "SCG Packaging", Sector.MATERIALS, Market.THAILAND, True),
    Stock("SIRI.BK", "Sansiri", Sector.REAL_ESTATE, Market.THAILAND, False),
    Stock("SPALI.BK", "Supalai", Sector.REAL_ESTATE, Market.THAILAND, False),
    Stock("SPRC.BK", "Star Petroleum", Sector.ENERGY, Market.THAILAND, False),
    Stock("STA.BK", "Sri Trang Agro", Sector.MATERIALS, Market.THAILAND, False),
    Stock("STGT.BK", "Sri Trang Gloves", Sector.MATERIALS, Market.THAILAND, False),
    Stock("TASCO.BK", "TIPCO Asphalt", Sector.MATERIALS, Market.THAILAND, False),
    Stock("TCAP.BK", "Thanachart Capital", Sector.FINANCIALS, Market.THAILAND, False),
    Stock("TIDLOR.BK", "Tidlor", Sector.FINANCIALS, Market.THAILAND, False),
    Stock("TISCO.BK", "TISCO Financial", Sector.FINANCIALS, Market.THAILAND, True),
    Stock("TLI.BK", "Thai Life Insurance", Sector.FINANCIALS, Market.THAILAND, True),
    Stock("TOP.BK", "Thai Oil", Sector.ENERGY, Market.THAILAND, True),
    Stock("TRUE.BK", "True Corporation", Sector.COMMUNICATIONS, Market.THAILAND, True),
    Stock("TTB.BK", "TMBThanachart Bank", Sector.FINANCIALS, Market.THAILAND, True),
    Stock("TU.BK", "Thai Union", Sector.CONSUMER, Market.THAILAND, True),
    Stock("VGI.BK", "VGI Global Media", Sector.COMMUNICATIONS, Market.THAILAND, True),
    Stock("WHA.BK", "WHA Corporation", Sector.REAL_ESTATE, Market.THAILAND, True),
]

# SET50 - Official constituents (subset of SET100 with is_major=True)
# The SET50 list is already marked with is_major=True in SET100_STOCKS above


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_universe(name: str) -> List[Stock]:
    """Get stocks for a specific universe"""
    universes = {
        "sp500": SP500_STOCKS,
        "sp50": [s for s in SP500_STOCKS if s.is_major],
        "set100": SET100_STOCKS,
        "set50": [s for s in SET100_STOCKS if s.is_major],
    }
    return universes.get(name.lower(), SP500_STOCKS)


def get_tickers(universe: str) -> List[str]:
    """Get list of ticker symbols for a universe"""
    return [s.ticker for s in get_universe(universe)]


def get_stock_info(ticker: str) -> Optional[Stock]:
    """Get stock info by ticker"""
    all_stocks = SP500_STOCKS + SET100_STOCKS
    for stock in all_stocks:
        if stock.ticker == ticker:
            return stock
    return None


def get_universe_summary(universe: str) -> Dict:
    """Get summary of a universe"""
    stocks = get_universe(universe)
    sectors = {}
    for s in stocks:
        sector_name = s.sector.value
        sectors[sector_name] = sectors.get(sector_name, 0) + 1
    
    return {
        "name": universe,
        "total_stocks": len(stocks),
        "major_stocks": len([s for s in stocks if s.is_major]),
        "sectors": sectors,
        "market": stocks[0].market.value if stocks else "Unknown"
    }


def get_available_universes() -> List[Dict]:
    """List all available universes"""
    return [
        {"id": "sp500", "name": "S&P 500 (Top 80)", "market": "US", "count": len(SP500_STOCKS)},
        {"id": "sp50", "name": "S&P 50 (Mega Cap)", "market": "US", "count": len([s for s in SP500_STOCKS if s.is_major])},
        {"id": "set100", "name": "SET100 (Thailand)", "market": "Thailand", "count": len(SET100_STOCKS)},
        {"id": "set50", "name": "SET50 (Thailand Large Cap)", "market": "Thailand", "count": len([s for s in SET100_STOCKS if s.is_major])},
    ]
