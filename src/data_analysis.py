import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

from data_manager import SymbolData
from global_constants import HIST_DATA_YEARS

def determine_exp_trend(data: pd.Series, 
                                r2_threshold=0.8) -> tuple[bool, float, np.ndarray]:
    """Use an exponential regression to determine if a series of data points in 
    the form (x, y) follows a strong, positive exponential trend. (R^2 >= 0.8)

    Args:
        data (pd.Series): The datestamped historical close data for a symbol.
        r2_threshold (float, optional): The threshold of goodness of fit (R^2) 
        which must be met to consider the stock as following an exponential
        grwoth trend.
    
    Returns:
        bool: Whether or not the symbol shows a historical exponential trend.
        float: The R^2 value of the exponentnial regresion (if applicable)
        np.ndarray: A series of values corresponding to each day of historical
        close data containing the predicted price from the exponential 
        regression.
    """
    data = data.dropna() # remove NaNs or missing values
    time_index = np.arange(len(data)).reshape(-1, 1)
    log_prices = np.log(data.values).reshape(-1, 1)
    
    model = LinearRegression()
    model.fit(time_index, log_prices)
    
    # Use model to predict a value at each point
    predicted_log_prices = model.predict(time_index)
    # Create the LSRL and get an R^2
    r2 = r2_score(log_prices, predicted_log_prices)
    slope = model.coef_[0][0]  # Extract the slope from the model

    if r2 >= r2_threshold and slope > 0:
        predicted_prices = np.exp(predicted_log_prices)
        return (True, r2, predicted_prices)
    else:
        return (False, None, None)

def determine_cagr(data: pd.Series, years: float) -> float:
    """Determine the CAGR (cumulative average growth rate) of the symbol given
    its historical close data.

    Args:
        data (pd.Series): The historical close data
        years (float): The period of time spanned by the historical close data
    """
    initial_price = data.iloc[0][0]
    final_price = data.iloc[-1][0]
    return (final_price / initial_price) ** (1/years) - 1

def save_plot_img(data: dict, ticker_symbol: str, 
                  predicted_prices: np.ndarray) -> str:
    """Save a MatPlotLib generated graph of the stock's historical performance
    with an exponential trendline. Image saved as a PNG file for use in the PDF
    report.
    
    Args:
        data (dict): The historical close data for the symbol.
        ticker_symbol (str): The symbol.
        predicted_prices (str): The predicted prices corresponding to each
        value in data.
    """
    chart_path = f"charts/{ticker_symbol}_chart.png"
    os.makedirs('charts', exist_ok=True)
    
    plt.figure(figsize=(10, 6))
    plt.title(ticker_symbol)
    plt.plot(data.index, data.values, label='Actual Price')
    plt.plot(data.index, predicted_prices, label='Exponential Trend Line', 
             linestyle='--')
    plt.xlabel("Date")
    plt.ylabel("Adj. Close Price")
    plt.legend()

    plt.savefig(chart_path)
    plt.close()

    return chart_path

def analyse_symbols(symbol_data_list: list[SymbolData]) -> None:
    """Perform data analysis on each of the SymbolData to determine if the stock
    price exhibits an exponential trend.

    Args:
        symbol_data_list (list[SymbolData]): The list of SmybolData to analyze.
    """
    for symbol_data in symbol_data_list:
        is_exponential, r2, predicted_values = determine_exp_trend(
            symbol_data.symbol_hist_data)
        if is_exponential:
            save_plot_img(symbol_data.symbol_hist_data, 
                          symbol_data.symbol_info["symbol"],
                          predicted_values)
            symbol_data.r2 = r2
            symbol_data.cagr = determine_cagr(symbol_data.symbol_hist_data, 
                                              HIST_DATA_YEARS)