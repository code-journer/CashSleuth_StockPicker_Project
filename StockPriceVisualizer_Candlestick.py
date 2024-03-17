"""
Title: Eric Cantrell's Stock Picker Project

Description: A Python tool for fetching and visualizing historical stock price using a candlestick chart, Yahoo Finance API and Matplotlib.

Author: Eric Cantrell
Date: March 17, 2024

"""

# Importing the 'datetime' module for handling date and time operations
from datetime import datetime, timedelta
# Importing pandas library as 'pd' for data manipulation and analysis
import pandas as pd
# Importing 'yfinance' library as 'yf' for fetching financial data, stock market information, from Yahoo Finance.
import yfinance as yf
# Importing mplfinance library for candlestick chart plotting
import mplfinance as mpf
from mplfinance import make_marketcolors
# Importing matplotlib.pyplot for general plotting
import matplotlib.pyplot as plt
# Importing the 'relativedelta' class from the 'dateutil.relativedelta' module for relative date calculations.
from dateutil.relativedelta import relativedelta

# Initializing ticker symbol
ticker_symbol = None

while True:
    ticker_symbol = input("Please enter the stock symbol: ").upper()
    error_message = None

    try:
        # Attempting to fetch historical data for the entered symbol to check its validity
        historical_data = yf.Ticker(ticker_symbol).history(period="1d")
        # Converting the index to DatetimeIndex
        historical_data.index = pd.to_datetime(historical_data.index)

        if historical_data.empty:
            error_message = f"{ticker_symbol}: No data found, symbol may be delisted."
            raise ValueError(error_message)

        break  # Breaking out of the loop if the symbol has data available

    except ValueError as e:
        if error_message is None:
            error_message = str(e)
            print(f"{error_message}")
        try_again = input("Do you want to try again? (yes/no): ").lower()
        if try_again != 'yes':
            print("Exiting program.")
            exit()

# Function to get date from user input
def get_date_from_user(prompt):
    while True:
        user_input = input(prompt)
        if not user_input:
            return None
        try:
            return datetime.strptime(user_input, "%m/%d/%y").date()
        except ValueError:
            print("Invalid date format. Please use mm/dd/yy.")

try:

    # Prompting user for start and end dates
    today = datetime.now().date()

    # Parsing start date
    start_date_input = get_date_from_user(
        "Please enter the start date using mm/dd/yy format (or press enter for a year before today): ")
    start_date = start_date_input or (today - relativedelta(months=3))

    # Parsing end date
    end_date_input = get_date_from_user(
        "Please enter the end date using mm/dd/yy format (or press enter for today's date): ")
    end_date = end_date_input or today - timedelta(days=1)

    # Fetching data for the entered symbol
    ticker_data = yf.download(ticker_symbol, start=start_date, end=end_date)

    # Checking for NaN or missing values
    print("NaN or missing values:", ticker_data.isna().sum().sum())

    # Setting 'Date' as a DatetimeIndex
    if 'Date' in ticker_data.columns:
        ticker_data.index = pd.to_datetime(ticker_data.index, errors='coerce')

    # Ensuring 'Date' column is in datetime format and set as index
    if 'Date' in ticker_data.columns:
        if not isinstance(ticker_data.index, pd.DatetimeIndex):
            print("Converting 'Date' column to datetime format.")
            ticker_data['Date'] = pd.to_datetime(ticker_data['Date'])
        ticker_data.set_index('Date', inplace=True)
        # Using if 'Date' column is not needed anymore
        ticker_data.drop('Date', axis=1, inplace=True)

    # Converting all columns in the DataFrame to numeric data types
    ticker_data = ticker_data.apply(pd.to_numeric, errors='coerce').round(2)

    # Handling NaN values introduced during the conversion process by filling them with 0
    ticker_data.fillna(0, inplace=True)

    # Saving the cleaned data to CSV files
    ticker_data.to_csv(f'{ticker_symbol}_stock_data_Indexed.csv', index=True)

    # Assuming your DatetimeIndex is named 'Date'
    ticker_data.index = ticker_data.index.date  # Converting DatetimeIndex to DateIndex

    # Ensuring 'Date' is in datetime format and set as index
    if not isinstance(ticker_data.index, pd.DatetimeIndex):
        print("Converting 'Date' column to datetime format.")
        ticker_data.index = pd.to_datetime(ticker_data.index)  # Convert index

    # Defining market colors with custom up and down colors
    marketcolors = {
        "up": "green",
        "down": "red",
        "edge": "black",  # Edge color of candlestick bars
        "wick": "inherit",  # Wick color
        "volume": "inherit",  # Volume bars color
    }

    #  Marketcolors dictionary
    mc = make_marketcolors(up=marketcolors["up"], down=marketcolors["down"], inherit=True)

    # Style dictionary
    style = mpf.make_mpf_style(marketcolors=mc)

    # Plotting the candlestick chart using mplfinance
    try:
        mpf.plot(ticker_data, type='candle', volume=True, style=style, figsize=(16, 10))
        plt.savefig('candlestick_plot.png')  # Save the plot as a PNG file
        print("Plotting successful! The plot has been saved as 'candlestick_plot.png'.")
    except Exception as e:
        print("Error during plotting:", e)

#  Exiting program or taking action based on error; for now, the program will proceed with empty DataFrame.
except ValueError as e:
    print(f"Error: {e}. Please make sure the entered symbol '{ticker_symbol}' is valid.")