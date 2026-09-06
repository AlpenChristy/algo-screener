"""
FYERS v3 - HDFC Bank historical data test

What this script does:
1. Opens the FYERS authorization page in your browser.
2. You log in and authorize the app.
3. You paste the auth_code from the redirect URL.
4. The script exchanges it for an access token.
5. It fetches daily historical OHLCV data for HDFC Bank.
6. It prints the latest rows and saves the data to hdfcbank_daily.csv.

Install:
    pip install fyers-apiv3 pandas

Before running:
    - Create a FYERS API v3 app.
    - Put your App ID, Secret Key and Redirect URI below.
    - The Redirect URI must exactly match the one configured in FYERS.
"""

import webbrowser
import pandas as pd
from fyers_apiv3 import fyersModel


# ============================================================
# 1. YOUR FYERS APP DETAILS
# ============================================================

CLIENT_ID = "ZK21D3U8W7-100"
SECRET_KEY = "5W5RTU1N2Q"
REDIRECT_URI = "https://fyers.in"


# ============================================================
# 2. STOCK + DATE SETTINGS
# ============================================================

SYMBOL = "NSE:HDFCBANK-EQ"

# Daily candles
RESOLUTION = "D"

# Change these dates as required.
START_DATE = "2025-01-01"
END_DATE = "2026-08-31"


# ============================================================
# 3. AUTHENTICATION
# ============================================================

def authenticate():
    print("\nCreating FYERS authorization URL...")

    session = fyersModel.SessionModel(
        client_id=CLIENT_ID,
        secret_key=SECRET_KEY,
        redirect_uri=REDIRECT_URI,
        response_type="code",
        grant_type="authorization_code",
        state="hdfcbank_test"
    )

    auth_url = session.generate_authcode()

    print("\nOpening browser...")
    print("\nIf it does not open automatically, copy this URL:\n")
    print(auth_url)

    webbrowser.open(auth_url)

    print("\nAfter you log in and authorize the app,")
    print("FYERS will redirect you to your Redirect URI.")

    auth_code = input(
        "\nPaste the value of 'auth_code' from the redirected URL:\n> "
    ).strip()

    if not auth_code:
        raise ValueError("No auth_code was provided.")

    session.set_token(auth_code)

    print("\nExchanging auth_code for access token...")

    response = session.generate_token()

    if response.get("s") != "ok":
        raise RuntimeError(
            f"Failed to generate access token:\n{response}"
        )

    return response["access_token"]


# ============================================================
# 4. FETCH HISTORICAL DATA
# ============================================================

def fetch_historical_data(access_token):

    fyers = fyersModel.FyersModel(
        client_id=CLIENT_ID,
        token=access_token,
        is_async=False,
        log_path=""
    )

    start = pd.Timestamp(START_DATE)
    end = pd.Timestamp(END_DATE)

    all_candles = []

    # FYERS allows max 366 days for D/1W/1M resolutions.
    max_days = 365

    current_start = start

    while current_start <= end:

        current_end = min(
            current_start + pd.Timedelta(days=max_days),
            end
        )

        data = {
            "symbol": SYMBOL,
            "resolution": RESOLUTION,
            "date_format": "1",
            "range_from": current_start.strftime("%Y-%m-%d"),
            "range_to": current_end.strftime("%Y-%m-%d"),
            "cont_flag": "1"
        }

        print(
            f"\nFetching: "
            f"{data['range_from']} -> {data['range_to']}"
        )

        response = fyers.history(data=data)

        if response.get("s") != "ok":
            raise RuntimeError(
                f"FYERS history API error:\n{response}"
            )

        candles = response.get("candles", [])

        print(f"Received {len(candles)} candles")

        all_candles.extend(candles)

        # Move to the next day so we don't request
        # the same boundary date twice.
        current_start = current_end + pd.Timedelta(days=1)

    if not all_candles:
        raise RuntimeError("FYERS returned no candle data.")

    df = pd.DataFrame(
        all_candles,
        columns=[
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]
    )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        unit="s"
    )

    # Remove any accidental duplicates
    df = df.drop_duplicates(
        subset=["timestamp"]
    )

    # Make sure everything is chronological
    df = df.sort_values(
        "timestamp"
    ).reset_index(drop=True)

    return df

# ============================================================
# 5. MAIN
# ============================================================

def main():

    if "YOUR_" in CLIENT_ID or "YOUR_" in SECRET_KEY:
        raise ValueError(
            "Please enter your FYERS CLIENT_ID, SECRET_KEY "
            "and REDIRECT_URI at the top of the file."
        )

    access_token = authenticate()

    print("\nAuthentication successful.")

    df = fetch_historical_data(access_token)

    print("\n" + "=" * 80)
    print("HDFC BANK - HISTORICAL DATA")
    print("=" * 80)

    print(f"\nTotal candles received: {len(df)}")

    print("\nLatest 10 rows:\n")
    print(df.tail(10).to_string(index=False))

    # Save CSV
    output_file = "hdfcbank_daily.csv"
    df.to_csv(output_file, index=False)

    print(f"\nSaved data to: {output_file}")

    print("\nDone.")


if __name__ == "__main__":
    main()
