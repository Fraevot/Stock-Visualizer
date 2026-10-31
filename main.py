import requests
import pandas as pd
from datetime import datetime
import plotly.express as px

API_KEY = "Z44DR7L1TCPO0BOR"
BASE_URL = "https://www.alphavantage.co/query"

def get_user_input():
    symbol = input("Enter stock symbol (example: AAPL): ").strip().upper()

    while not symbol:
        symbol = input("Enter a valid stock symbol (example: AAPL): ").strip().upper()

    chart_types = {
        "1": "Bar",
        "2": "Line"
    }

    print("\nSelect chart type:")
    print("1. Bar")
    print("2. Line")

    chart_choice = input("Enter choice (1-2): ").strip()

    while chart_choice not in chart_types:
        chart_choice = input("invalid choice. Enter 1, 2, or 3: ").strip()

    functions = {
        "1": "TIME_SERIES_INTRADAY",
        "2": "TIME_SERIES_DAILY",
        "3": "TIME_SERIES_WEEKLY",
        "4": "TIME_SERIES_MONTHLY"
    }

    print("\nSelect time series type:")
    print("1. Intraday")
    print("2. Daily")
    print("3. Weekly")
    print("4. Monthly")

    function_choice = input("Enter choice (1-4): ").strip()

    while function_choice not in functions:
        function_choice = input("Invalid choice. Enter 1, 2, 3, or 4: ").strip()

    interval = None

    if function_choice == "1":
        intervals = {
            "1": "1min",
            "2": "5min",
            "3": "15min",
            "4": "30min",
            "5": "60min",
        }

        print("\nSelect intraday interval:")
        print("1. 1 minute")
        print("2. 5 minutes")
        print("3. 15 minutes")
        print("4. 30 minutes")
        print("5. 60 minutes")

        interval_choice = input("Enter choice (1-5): ").strip()

        while interval_choice not in intervals:
            interval_choice = input("Invalid choice. Enter 1-5: ").strip()

        interval = intervals[interval_choice]
    
    start_date = get_valid_date("Enter the start date (YYYY-MM-DD): ")
    end_date = get_valid_date("Enter the end date (YYYY-MM-DD): ")

    while end_date < start_date:
        print("Error: End date cannot be before start date.")
        end_date = get_valid_date("Enter end date again (YYYY-MM-DD): ")

    return (
        symbol,
        chart_types[chart_choice],
        functions[function_choice],
        interval,
        start_date,
        end_date
    )

def get_valid_date(prompt):
    while True:
        date_str = input(prompt).strip()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD format.")

def get_stock_data(symbol, function, interval=None):

    parameters = {
        "function": function,
        "symbol": symbol,
        "outputsize": "full",
        "apikey": API_KEY
    }

    if function == "TIME_SERIES_INTRADAY":
        parameters["interval"] = interval

    try:
        response = requests.get(
            url=BASE_URL,
            params=parameters,
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

    except requests.RequestException as error:
        print("Error connecting to Alpha Vantage:", error)
        return None

    if "Error Message" in data:
        print("API Error:", data["Error Message"])
        return None
    
    if "Note" in data:
        print("API limit message:", data["Note"])
        return None

    if "Information" in data:
        print("API Information", data["Information"])
        return None

    time_series_key = next(
        (key for key in data if "Time Series" in key),
        None
    )

    if time_series_key is None:
        print("No stock data was returned.")
        return None

    df = pd.DataFrame.from_dict(
        data[time_series_key],
        orient="index"
    )

    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    df.columns = [
        column.split(". ", 1)[-1].lower()
        for column in df.columns
    ]

    for column in df.columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df

def filter_dates(df, start_date, end_date):
    mask = (df.index >= start_date) & (df.index <= end_date)
    return df.loc[mask]

def create_chart(df, symbol, chart_type, start_date, end_date):
    if df.empty:
        print("No stock data available to create a chart.")
        return None

    if "close" not in df.columns:
        print("No closing prices found.")
        return None

    title = f"{symbol} Stock Prices ({start_date} to {end_date})"

    if chart_type == "Bar":
        chart = px.bar(df, x=df.index, y="close", title=title)
    elif chart_type == "Line":
        chart = px.line(df, x=df.index, y="close", title=title)
    else:
        print("Invalid chart type.")
        return None

    chart.update_layout(
        xaxis_title="Date",
        yaxis_title="Closing Price ($)"
    )

    return chart

def main():
    print("             Stock Data Visualizer")
    print("______________________________________")

    (symbol, chart_type, function, interval, start_date, end_date) = get_user_input()

    print("\nRetrieving stock data...")

    stock_data = get_stock_data(symbol,function,interval)
    
    if stock_data is None:
        return

    filtered_data = filter_dates(stock_data,start_date,end_date)

    if filtered_data is None:
        return

    chart = create_chart(filtered_data,symbol,chart_type,start_date,end_date)

    if chart is not None:
        chart.show()

if __name__ == "__main__":
    main()