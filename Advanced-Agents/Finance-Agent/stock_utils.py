import json
import yfinance as yf


def get_current_stock_price(ticker: str) -> str:
    """Get current stock price and basic info."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Try intraday first
        try:
            hist = stock.history(period="1d", interval="1m")
            if not hist.empty:
                current_price = float(hist["Close"].iloc[-1])
                current_volume = int(hist["Volume"].iloc[-1])
                current_time = hist.index[-1]
            else:
                raise ValueError("Empty intraday history")
        except Exception:
            # Fallback to daily
            hist = stock.history(period="5d", interval="1d")
            if not hist.empty:
                current_price = float(hist["Close"].iloc[-1])
                current_volume = int(hist["Volume"].iloc[-1])
                current_time = hist.index[-1]
            else:
                return f"Could not retrieve current price for {ticker}"

        prev_close = float(info.get("previousClose") or current_price)
        change_amount = current_price - prev_close
        change_pct = (change_amount / prev_close * 100.0) if prev_close else 0.0
        market_cap = info.get("marketCap")
        pe_ratio = info.get("trailingPE")

        result = {
            "ticker": ticker.upper(),
            "current_price": round(current_price, 2),
            "previous_close": round(prev_close, 2),
            "change_amount": round(change_amount, 2),
            "change_percent": round(change_pct, 2),
            "current_volume": int(current_volume) if current_volume else 0,
            "market_cap": int(market_cap) if market_cap else 0,
            "pe_ratio": round(pe_ratio, 2) if pe_ratio else None,
            "company": info.get("longName", ticker),
            "sector": info.get("sector", "Unknown"),
            "timestamp": getattr(current_time, "isoformat", lambda: str(current_time))(),
        }
        return json.dumps(result)
    except Exception as e:
        return f"Error getting current stock price for {ticker}: {str(e)}"


def get_historical_stock_data(ticker: str, time_frame: str = "3mo") -> str:
    """
    Get stock data for a specified time frame for trend analysis.
    time_frame: one of 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max.
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=time_frame)

        if hist.empty:
            return f"Could not retrieve {time_frame} data for {ticker}"

        start_price = float(hist["Close"].iloc[0])
        end_price = float(hist["Close"].iloc[-1])
        high_price = float(hist["High"].max())
        low_price = float(hist["Low"].min())
        avg_volume = float(hist["Volume"].mean()) if "Volume" in hist else 0.0
        trend = (end_price - start_price) / start_price * 100.0 if start_price else 0.0
        volatility = float(hist["Close"].std())

        result = {
            "ticker": ticker.upper(),
            "period": time_frame,
            "start_price": round(start_price, 2),
            "end_price": round(end_price, 2),
            "high_price": round(high_price, 2),
            "low_price": round(low_price, 2),
            "trend": round(trend, 2),
            "volatility": round(volatility, 2),
            "avg_volume": int(avg_volume) if avg_volume else 0,
        }
        return json.dumps(result)
    except Exception as e:
        return f"Error getting historical data for {ticker}: {str(e)}"