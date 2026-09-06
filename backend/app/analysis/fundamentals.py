from typing import Dict, Any, Optional

def analyze_fundamentals(ticker_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract fundamental metrics from ticker metadata dictionary.
    """
    if not ticker_info:
        return {}

    return {
        "market_cap": ticker_info.get("marketCap"),
        "pe_ratio": ticker_info.get("trailingPE"),
        "pb_ratio": ticker_info.get("priceToBook"),
        "dividend_yield": ticker_info.get("dividendYield"),
        "earnings_growth": ticker_info.get("earningsGrowth"),
        "revenue_growth": ticker_info.get("revenueGrowth"),
        "float_shares": ticker_info.get("floatShares"),
        "shares_outstanding": ticker_info.get("sharesOutstanding"),
    }
