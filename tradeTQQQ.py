from zipline.api import schedule_function, date_rules, time_rules, order_target, record, symbol, set_benchmark
from zipline.pipeline import Pipeline
from zipline.pipeline.data import USEquityPricing
from zipline.pipeline.factors import AverageDollarVolume, RSI, BollingerBands
from zipline.finance.trading import TradingEnvironment
import math
import pandas
import matplotlib.pyplot as plt

def initialize(context):

    # Schedule our rebalance function to run at the start of
    # each week, when the market opens.
    schedule_function(
        func=my_rebalance,
        date_rule=date_rules.every_day(),
        time_rule=time_rules.market_open()
    )

def handle_data(context,data):
    
    # Data window
    window = 14
    
    # Get TQQQ prices
    price = data.history(symbol('TQQQ'), ['price'], window, '1d')
    latest_close = price['close'][-1]
    
    # Calculate RSI
    rsi = talib.RSI(price['close'][symbol('TQQQ')], timeperiod=window)
    
    # Calculate Bollinger Bands
    bbHigh, bbMid, bbLow = talib.BBANDS(close, timeperiod=window, nbdevup=2, nbdevdn=2, matype=0)
    
    rsiOverbought = rsi > 70
    rsiOversold = rsi < 30

    bbOverbought = latest_close > bbHigh
    bbOversold = latest_close < bbLow

    context.overbought = rsiOverbought & bbOverbought
    context.oversold = rsiOversold & bbOversold
    
def my_rebalance(context, data):
    """
    Rebalance daily.
    """

    if data.can_trade(symbol('TQQQ')):
        if context.oversold:
            order_target_percent(symbol('TQQQ'),1)
        elif context.overbought:
            order_target_percent(symbol('TQQQ'),0)
	
def analyze(context, perf):
    #for item in perf.items():
        #print(item,"\n")

    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    perf.excess_return.plot(ax=ax1)
    perf.benchmark_period_return.plot(ax=ax1)
    ax1.set_ylabel('returns')
    plt.legend(loc=0, labels=['Algorithm', 'Benchmark'])
    
    ax2 = fig.add_subplot(212)
    perf.portfolio_value.plot(ax=ax2)
    plt.ylabel('portfolio value in $')
    plt.show()