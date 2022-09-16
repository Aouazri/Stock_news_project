import requests
import datetime as dt
from twilio.rest import Client

# twilio info
twilio_phone_number = 'your twilio phone number'
account_sid = 'your account sid'
auth_token = 'your auth token'

# Company we're interested in
STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
# APIs
stock_api_key = "your stock api"
news_api_key = "your news api"
# ENDPOINTs
alphavantage_endpoint = "https://www.alphavantage.co/query"
news_endpoint = "https://newsapi.org/v2/everything"
# Parameters
stock_parameters = {
    "function": 'TIME_SERIES_DAILY',
    "symbol": STOCK,
    "apikey": stock_api_key,
}

## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

response = requests.get(alphavantage_endpoint, params=stock_parameters)
response.raise_for_status()
data = response.json()['Time Series (Daily)']
# Get the previous day using the datetime module
date = dt.datetime.now()
# previous date
stock_day = dt.datetime.today() - dt.timedelta(days=1)
stock_day_formatted = stock_day.strftime('%Y-%m-%d')
# previous date to the previous date
previous_stock_day = stock_day - dt.timedelta(days=1)
previous_stock_day_formatted = previous_stock_day.strftime('%Y-%m-%d')

# close values for the stock day and the previous stock day values
stock_day_close = data[stock_day_formatted]['4. close']
previous_stock_day_close = data[previous_stock_day_formatted]['4. close']

# percentage of stock fluctuation
stock_fluctuation = ((float(stock_day_close) - float(previous_stock_day_close)) * 100) / float(stock_day_close)
# formatting for the fluctuation percentage
if stock_fluctuation >= 0:
    fluctuation_message = f"🔺{round(stock_fluctuation, 2)}%"
else:
    fluctuation_message = f"🔻{abs(round(stock_fluctuation, 2))}%"

## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.
news_parameters = {
    'apiKey': news_api_key,
    'q': COMPANY_NAME,
    'searchIn': 'title,description',
    'from': previous_stock_day_formatted,
}
send_message = False
if abs(stock_fluctuation) >= 3:
    send_message = True
    response = requests.get(news_endpoint, params=news_parameters)
    data = response.json()['articles']
    titles = []
    descriptions = []
    for key in range(0, 3):
        titles.append(data[key]['title'])
        descriptions.append(data[key]['description'])
## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 
client = Client(account_sid, auth_token)
if send_message:
    message = client.messages \
        .create(
        body=f"""
            {STOCK}: {fluctuation_message}
             Headline 1: {titles[0]}.
             Brief: {descriptions[0]}
             Headline 2: {titles[1]}.
             Brief: {descriptions[1]}
             Headline 3: {titles[2]}.
             Brief: {descriptions[2]}
                """,
        from_=twilio_phone_number,
        to='your phone number'
    )
    print(message.status)

# Optional: Format the SMS message like this:
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""
