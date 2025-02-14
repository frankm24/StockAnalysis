from datetime import datetime
from dateutil.relativedelta import relativedelta
import yfinance as yf
import pickle
from dataclasses import dataclass
from time import sleep

import finnhub_client
from global_constants import HIST_DATA_YEARS

@dataclass
class SymbolData:
    """Dataclass containing the info and statistics, historical data, and 
    exponential fit results for a stock symbol.
    
    Attributes:
        symbol_info (dict): Basic info about the company behind the stock symbol
        symbol_hist_data (dict): Historical close data for the stock symbol
        r2 (float): R^2 value (goodness of fit) of the exponential regression
        performed on the model
        cagr (float): The CAGR (Cumulative Average Growth Rate) of the company's
        stock price. The avaerage % change in the stock price each year.
    """
    symbol_info: dict
    symbol_hist_data: dict
    r2: float
    cagr: float

CACHE_FILENAME = "cache.pkl"
REQUEST_DELAY = 2

def cache_symbol_data(symbol_data_list: list[SymbolData]) -> None:
    """Write a list of SymbolData to a file in the user's system to save data
    for future use. 
    
    Args: 
        symbol_data_list (list[SymbolData]): The list of SymbolData to save
    Returns:
        None
    """
    with open(CACHE_FILENAME, "wb") as file:
        pickle.dump(symbol_data_list, file)

def load_cached_symbol_data() -> list[SymbolData]:
    """Load the previously written SymbolData in the cache file, located at a
    hard-coded path.

    Args: 
        None
    Returns:
        list[SymbolData]: The list of SymbolData from the cache file
    """
    with open(CACHE_FILENAME, "rb") as file:
        return pickle.load(file)

def validate_and_get_info(ticker_symbol: str) -> tuple[bool, yf.Ticker]:
    """Lookup a ticker symbol using the Yahoo Finance scraping library to
    determine if the symbol is currently listed and trading on the market 
    (valid). If the symbol is valid, return a yf.Ticker object for further
    data collection.

    Args:
        ticker_symbol (str): The symbol to validate
    Returns:
        tuple[bool, yf.Ticker | None]: A tuple containing a boolean representing 
        if the stock is valid or not, and either a yf.Ticker for the valid 
        symbol or None.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        sleep(REQUEST_DELAY)
        data = ticker.history(period="1d")
        if data.empty:
            print(f"""{ticker_symbol}: No price history available. 
                  Invalid or delisted ticker.""")
            return (False, None)
        return (True, ticker.get_info())
    except Exception as e:
        print(f"{ticker_symbol}: Validation failed due to error: {e}")
        return (False, None)

def get_historical_close_data(ticker_symbol: str, 
                              period_years=HIST_DATA_YEARS) -> dict | None:
    """Get the historical close data for a stock symbol over a default period
    of 5 years using the Yahoo Finance scraper.

    Args:
        ticker_symbol (str): The ticker symbol to retrieve data for
        period_years (int, optional): The length of the period to retrieve 
        historical close data from
    Returns:
        dict | None: A dictionary containing the historical close data
    """
    today = datetime.now().date()
    five_years_ago = today - relativedelta(years=period_years)

    today_formatted = today.strftime("%Y-%m-%d")    
    five_years_ago_formatted = five_years_ago.strftime("%Y-%m-%d")   

    try:
        data = yf.download(ticker_symbol, start=five_years_ago_formatted, 
                           end=today_formatted)
        sleep(REQUEST_DELAY)
        if data.empty:
            raise ValueError(f"No data found for symbol: {ticker_symbol}")
            return None
        price_column = "Adj Close" if "Adj Close" in data.columns else "Close"
        return data[price_column]
    except Exception as e:
        print(f"Error fetching data for {ticker_symbol}: {e}")
        return None

def get_and_cache_data(num_symbols: int) -> list[SymbolData]:
    """Search for, retrieve, and cache data on stock symbols from the random
    list given by the Finnhub API. Search through a maximum of num_symbols
    symbols, validating each one. The number of valid symbols and therefore
    length of the return list is not gaurenteed, dependent on the number of
    valid symbols.

    Args:
        num_symbols (int): The number of symbols to search through before 
        returning.
    Returns:
        list[SymbolData]: A list of SymbolData for each valid stock symbol that
        was found
    """
    symbols = finnhub_client.get_symbols()
    symbol_data_list = []
    i = 0
    for symbol in symbols:
        if i == num_symbols:
            break
        symbol_string = symbol["displaySymbol"]
        is_valid, symbol_info = validate_and_get_info(symbol_string)
        if is_valid:
            hist_data = get_historical_close_data(symbol_string)
            if hist_data is not None:
                symbol_data = SymbolData(symbol_info, hist_data, 0., 0.)
                symbol_data_list.append(symbol_data)
                i += 1
            else:
                print(f"Yahoo Finance has no data for symbol: {symbol_string}.")
        else:
            print(f"Symbol {symbol_string} is invalid or delisted.")

    cache_symbol_data(symbol_data_list)
    return symbol_data_list

def get_symbol_data(read_from_cache: bool, num_symbols: int) -> list[SymbolData]:
    """Get data on stock symbols, either by searching through a maximum of 
    num_symbols symbols using the Finnhub API and Yahoo Finance scraper or by
    reading the cache file.

    Args:
        read_from_cache (bool): Whether to read from cache or to lookup a new
        set of symbols (and overwrite the cache with data for the new symbols)
        num_symbols (int): The maximum number of symbols to attempt to validate
        before stopping the stock symbol lookup process. 
    """
    if read_from_cache:
        return load_cached_symbol_data()
    return get_and_cache_data(num_symbols)