from formatting import *
from data_manager import get_symbol_data, SymbolData
from data_analysis import analyse_symbols
from report_generator import generate_report

def main():
    """The entry point into the program.
    """
    symbol_data = get_symbol_data(True, 100)
    analyse_symbols(symbol_data)
    generate_report(symbol_data)

if __name__ == "__main__":
    main()
    