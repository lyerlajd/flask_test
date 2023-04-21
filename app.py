import flask
import pygal
import requests
from flask import request, render_template, url_for
from alpha_vantage.timeseries import TimeSeries
from datetime import datetime

def compareDates(date1, date2):
   
    try:
       date1 = datetime.fromisoformat(date1)
       date2 = datetime.fromisoformat(date2)
    except:
        print("this is an error")

    if date1 <= date2:
        return True
    else:
        return False

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html')

@app.route('/chart', methods = ['POST'])
def chart():

    symbol = request.form['symbol']
    chart_type = request.form['chart_type']
    time_series = request.form['time_series']
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    # set the chart type

    if chart_type == "line":
        chart = pygal.Line(x_label_rotation=20)
    elif chart_type == "bar":
        chart = pygal.Bar()

    # get the url and return the data
    if time_series == "TIME_SERIES_INTRADAY":
        url = f'https://www.alphavantage.co/query?function={time_series}&symbol={symbol}&interval=15min&apikey=16M4EW4M4DAV8AZZ'
        r = requests.get(url)
        data = r.json()
        
        date_data = data['Time Series (15min)'] # any interval changes need to be here too

    elif (time_series == "TIME_SERIES_DAILY"): # this is a premium feature and does not work right now. if a premium key was used it would likely work
        url = f'https://www.alphavantage.co/query?function={time_series}&symbol={symbol}&apikey=16M4EW4M4DAV8AZZ'
        r = requests.get(url)
        data = r.json()

        date_data = data["Time Series (Daily)"]

    elif (time_series == "TIME_SERIES_WEEKLY"):
        url = f'https://www.alphavantage.co/query?function={time_series}&symbol={symbol}&apikey=16M4EW4M4DAV8AZZ'
        r = requests.get(url)
        data = r.json()

        date_data = data['Weekly Time Series']

    else: # function == TIME_SERIES_MONTHLY
        url = f'https://www.alphavantage.co/query?function={time_series}&symbol={symbol}&apikey=16M4EW4M4DAV8AZZ'
        r = requests.get(url)
        data = r.json()

        date_data = data['Monthly Time Series']    
    
    # configuring chart
    chart.title = f'{symbol} Stock Prices for ({start_date} - {end_date})'
    open = []
    high = []
    low = []
    close = []
    labels = []
    for date in date_data:
        if (compareDates(start_date, date) and compareDates(date, end_date)):
            print(date)
            print(date_data[date])
            open.append(float(date_data[date]['1. open']))
            high.append(float(date_data[date]['2. high']))
            low.append(float(date_data[date]['3. low']))
            close.append(float(date_data[date]['4. close']))
            labels.append(date)

    # reversing lists so that the graph actually goes left to right
    open.reverse()
    high.reverse()
    low.reverse()
    close.reverse()
    labels.reverse()

    chart.add('Open', open)
    chart.add('High', high)
    chart.add('Low', low)
    chart.add('Close', close)
    chart.x_labels = labels

    chart = chart.render_data_uri()

    return render_template('secondPage.html', symbol = symbol, chart_type = chart_type, time_series = time_series, start_date = start_date, end_date = end_date, chart = chart)

app.run()