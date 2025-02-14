import weasyprint
import os

from formatting import *
from data_manager import SymbolData

def generate_stock_html(ticker_info: dict, r2: float, cagr: float) -> str:
    """Generate a string of HTML representing pages of the PDF report for a 
    stock symbol using template.html,styles.css, and the provided arguments. 

    Args:
        ticker_info (dict): Basic qualitative info about the company behind the
        stock symbol.
        r2 (float): The R^2 value of the exponential regression performed in
        the data anlysis section.
        cagr (float): The CAGR (Cumulative Average Growth Rate) of the company's
        stock price over the period of the collected historical data.
    Returns: 
        str: The string of HTML for the company/stock
    """
    mkt_cap_formatted = format_money(ticker_info["marketCap"])
    todays_date_formatted = format_today()
    ticker_symbol = ticker_info["symbol"]
    chart_path = f"charts/{ticker_symbol}_chart.png"
    with open("template.html") as file:
        html_template = file.read()

    html_content = html_template.replace("{{ ticker_symbol }}", ticker_symbol)
    html_content = html_content.replace("{{ longName }}", 
                                        ticker_info["longName"])
    html_content = html_content.replace("{{ mkt_cap_formatted }}", 
                                        mkt_cap_formatted)
    html_content = html_content.replace("{{ longBusinessSummary }}",
                                        ticker_info["longBusinessSummary"])
    html_content = html_content.replace("{{ cagr }}", f"{cagr:.2%}")
    html_content = html_content.replace("{{ r2 }}", f"{r2:.3f}")
    html_content = html_content.replace("{{ todays_date }}",
                                        todays_date_formatted)
    html_content = html_content.replace("{{ full_address }}", format_address(
        ticker_info.get("address1"), ticker_info.get("address2"), 
        ticker_info.get("city"), ticker_info.get("state"),
        ticker_info.get("zip"), ticker_info.get("country")
    ))
    html_content = html_content.replace("{{ chart_path }}", 
                                        f"file://{os.path.abspath(chart_path)}")
    return html_content

def generate_report(symbol_data_list: list[SymbolData]) -> None:
    """Generate a PDF report for a list of SymbolData (companies). Save the 
    report to the reports directory.

    Args:
        symbol_data_list (list[SymbolData]): The list of SymbolData to generate
        the report about
    Returns:
        None
    """
    os.makedirs("reports", exist_ok=True)
    report_path = f"reports/{current_time()}.pdf" 
    report_html = ""
    page_count = len(symbol_data_list)
    for i, symbol_data in enumerate(symbol_data_list, start=1):
        if symbol_data.r2 != 0.0:
            symbol_html = generate_stock_html(symbol_data.symbol_info, 
                                              symbol_data.r2, symbol_data.cagr)
            report_html += symbol_html
    html = weasyprint.HTML(string=report_html)
    css = weasyprint.CSS(filename="styles.css")
    html.write_pdf(report_path, stylesheets=[css])
    print(f"PDF report saved to {report_path}")
        