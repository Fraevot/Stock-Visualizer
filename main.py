import requests
import pandas as pd

API_KEY = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=Y9FIZTAFCOT4JY38"

def get_user_input():
    symbol = input("Enter stock symbol (example: AAPL): ").strip().upper()

    if symbol == "":
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
        "1": "TIME_SERIES_DAILY",
        "2": "TIME_SERIES_WEEKLY",
        "3": "TIME_SERIES_MONTHLY"
    }

    print("\nSelect time series type:")
    print("1. Daily")
    print("2. Weekly")
    print("3. Monthly")

    function_choice = input("Enter choice (1-3): ").strip()

    while function_choice not in functions:
        function_choice = input("Invalid choice. Enter 1, 2, or 3: ").strip()

    start_date = input("Enter the start date (YYYY-MM-DD): ").strip("-")
    end_date = input("Enter the end date (YYYY-MM-DD): ").strip("-")

    """
        start_date = get_valid_date("Enter the start date (YYYY-MM-DD): ")
        end_date = get_valid_date("Enter the end date (YYYY-MM-DD): ")
    """

    while end_date < start_date:
        print("Error: End date cannot be before start date.")
        end_date = get_valid_date("Enter end date again (YYYY-MM-DD): ")

    return (
        symbol,
        chart_types[chart_choice],
        functions[function_choice],
        start_date,
        end_date
    )

def get_valid_date(prompt):
    # validates that the start date is before the end date
    pass

def get_stock_data(symbol, function):

    parameters = {
        "function": function,
        "symbol": symbol,
        "outputsize": "compact",
        "apikey": API_KEY
    }

    try:
        response = requests.get(
            url=API_KEY,
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
    # This function filters stock data to the requested date range
    pass

def create_chart(df, symbol, chart_type, start_date, end_date):
    # Generates the chart itself
    pass

def main():
    print("             Stock Data Visualizer")
    print("______________________________________")

    symbol, chart_type, function, start_date, end_date = (
        get_user_input()
    )

    print("\nRetrieving stock data...")

    stock_data = get_stock_data(symbol,function)
    
    if stock_data is None:
        return


if __name__ == "__main__":
    main()