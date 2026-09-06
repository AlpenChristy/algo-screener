from typing import Dict, Any

def calculate_signal_score(stock_res: Dict[str, Any]) -> float:
    """
    Score a stock signal based on distance to benchmark, volume expansion, and delivery percentage.
    Scores range from 0.0 to 100.0.
    """
    if not stock_res:
        return 0.0

    score = 50.0

    # Distance score (closer to benchmark level adds points)
    pct_dist = stock_res.get("pct_above_52w_low") or stock_res.get("pct_from_30_dma") or 10.0
    if abs(pct_dist) <= 1.0:
        score += 25.0
    elif abs(pct_dist) <= 2.5:
        score += 15.0
    elif abs(pct_dist) <= 5.0:
        score += 5.0

    # Volume spike bonus
    vol_mult = stock_res.get("volume_multiple") or 1.0
    if vol_mult >= 3.0:
        score += 20.0
    elif vol_mult >= 2.0:
        score += 10.0

    # Delivery % bonus
    delivery_pct = stock_res.get("delivery_pct") or 0.0
    if delivery_pct >= 60.0:
        score += 10.0

    return min(score, 100.0)
