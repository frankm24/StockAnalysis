from api_key import FINNHUB_KEY
import finnhub
import time

client = finnhub.Client(api_key=FINNHUB_KEY) 

# Unavailable - Premium
def get_close_data(symbol: str, period_years=5) -> list[float]:
    """(UNTESTED PREMIUM ACCESS ONLY) Get historical and split-adjusted close 
    data for a given stock symbol over a period of years (default 5) via the 
    finnhub API.

    Args:
        symbol (str): The stock symbol to lookup data for
        period_years (int, optional): The period to pull data from.
    Returns:
        list[float]: a list of close data points
    """
    seconds_in_a_year = 365*24*60*60
    current_unix_time = int(time.time())
    five_years_ago_unix_time = (current_unix_time - 
                                period_years * seconds_in_a_year)

    candle_data = client.stock_candles(symbol, 
                                       'D', 
                                       five_years_ago_unix_time, 
                                       current_unix_time)
    return candle_data.get('c', [])

def get_symbols() -> list[dict]:
    """Generate a list of stock symbols trading in US stock exchanges. Consists 
    of US-based companies and ADRs (American Depository Reciepts).
    Args:
        None
    Returns:
        list[dict]: A list of securities and some relevant information in JSON
        format
    """
    return client.stock_symbols("US", security_type=["Common Stock", "ADR"])