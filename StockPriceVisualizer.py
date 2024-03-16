"""
Stock Picker Project: Stock Price Visualizer

Description: Dynamic Stock Price Visualizer is a Python program for investors seeking insightful perspectives
in equity financial markets. Tool will allow users to retrieve and visualize historical stock data for multiple
symbols, aiding in trend analysis and decision-making.

Author: Eric Cantrell
Date: March 16, 2024

"""

# Importing pandas library as 'pd' for data manipulation and analysis
import pandas as pd
# Importing 'yfinance' library as 'yf' for fetching financial data, stock market information, from Yahoo Finance.
import yfinance as yf
# Importing 'matplotlib.pyplot' module as 'plt' for creating static, animated, and interactive visualizations in Python.
import matplotlib.pyplot as plt
# Importing 'matplotlib.dates' module as 'mdates' for working with date formatting and advanced date-related functions.
import matplotlib.dates as mdates
# Importing the 'datetime' module for handling date and time operations, and 'timedelta' for time duration calculations.
from datetime import datetime, timedelta
# Importing the 'relativedelta' class from the 'dateutil.relativedelta' module for relative date calculations.
from dateutil.relativedelta import relativedelta

# Initializing ticker symbol
ticker_symbol = None

while True:
    ticker_symbol = input("Please enter the stock symbol: ").upper()
    error_message = None

    try:
        print("Fetching data for symbol:", ticker_symbol)
        # Attempting to fetch historical data for the entered symbol to check its validity
        historical_data = yf.Ticker(ticker_symbol).history(period="1d")
        if historical_data.empty:
            error_message = f"{ticker_symbol}: No data found, symbol may be delisted."
            raise ValueError(error_message)

        print("Symbol found.")
        break  # Break out of the loop if the symbol has data available

    except ValueError as e:
        if error_message is None:
            error_message = str(e)
            print(f"{error_message}")
        try_again = input("Do you want to try again? (yes/no): ").lower()
        if try_again != 'yes':
            print("Exiting program.")
            break  # Break out of the loop instead of exiting the program

print("Loop exited.")

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

# Prompting user for start and end dates
today = datetime.now().date()
start_date = get_date_from_user("Please enter the start date using mm/dd/yy format (or press enter for a year before today): ") or (today - relativedelta(years=1))
end_date = get_date_from_user("Please enter the end date using mm/dd/yy format (or press enter for today's date): ") or (today - timedelta(days=1))

# Fetching data for the valid symbol
try:
    # Attempting to fetch data for the entered symbol
    ticker_data = yf.download(ticker_symbol, start=start_date, end=end_date)
    print(ticker_data)

# Choose to exit the program or take appropriate action based on the error; for now, the program will proceed with empty DataFrame.
except ValueError as e:
    print(f"Error: {e}. Please make sure the entered symbol '{ticker_symbol}' is valid.")

# Ensuring 'Date' column is datetime format and set as index
if 'Date' in ticker_data.columns:
    ticker_data.rename(columns={'index': 'Date'}, inplace=True)
    ticker_data.index = pd.to_datetime(ticker_data.index, errors='coerce')

# Converting all columns in the DataFrame to numeric data types
ticker_data = ticker_data.apply(pd.to_numeric, errors='coerce').round(2)

# Handling NaN values introduced during the conversion process by filling them with 0
ticker_data.fillna(0, inplace=True)

# Saving the cleaned data to CSV files
ticker_data.to_csv(f'{ticker_symbol}_stock_data_Indexed.csv', index=True)

# Assuming your DatetimeIndex is named 'Date'
ticker_data.index = ticker_data.index.date  # Converting DatetimeIndex to DateIndex

# Plotting the 'Open' and 'Close' prices for symbol
symbol_data = ticker_data.loc[(pd.to_datetime(ticker_data.index).date >= pd.Timestamp(start_date).date()) & (
        pd.to_datetime(ticker_data.index).date <= pd.Timestamp(end_date).date())]

# Plotting Open vs. Close for the current symbol
plt.figure(figsize=(16, 10))
padding_factor = 10
plt.plot(symbol_data.index, symbol_data['Open'] + padding_factor, label='Open', color='green')
plt.plot(symbol_data.index, symbol_data['Close'], label='Close', color='gold')
plt.subplots_adjust(bottom=0.15)  # Adjusting value to see x label

# Adding legend and labels
plt.legend()
plt.title(f'{ticker_symbol} Open vs. {ticker_symbol} Close Prices')
plt.xlabel('Date')
plt.ylabel('Price')

# Setting y-axis limits dynamically based on data range
min_value = max(0, symbol_data[['Open', 'Close']].min().min() - padding_factor)
max_value = symbol_data[['Open', 'Close']].max().max() + padding_factor
plt.ylim(min_value, max_value)

# Displaying dates at an angle with weekly intervals
plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))

# Rotating the date labels at a 45-degree angle and set padding
plt.xticks(rotation=90, ha='right', rotation_mode='anchor')
plt.tick_params(axis='x', which='major', pad=10)  # Adjusting the pad value

plt.show()
