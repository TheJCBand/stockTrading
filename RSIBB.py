from zipline.api import attach_pipeline, pipeline_output, schedule_function, date_rules, time_rules, order_target, record, symbol, set_benchmark
from zipline.pipeline import Pipeline
from zipline.pipeline.data import USEquityPricing
from zipline.pipeline.factors import AverageDollarVolume, RSI, BollingerBands
from zipline.finance.trading import TradingEnvironment
import math
import pandas
import matplotlib.pyplot as plt
import talib

def initialize(context):

    #set_benchmark(symbol("SPY"))
    
    # Schedule our rebalance function to run at the start of
    # each week, when the market opens.
    schedule_function(
        func=my_rebalance,
        date_rule=date_rules.every_day(),
        time_rule=time_rules.market_open()
    )

    # Record variables at the end of each day.
    schedule_function(
        func=my_record_vars,
        date_rule=date_rules.every_day(),
        time_rule=time_rules.market_open()
    )

    # Create our pipeline and attach it to our algorithm.
    my_pipe = make_pipeline()
    attach_pipeline(pipeline=my_pipe, name='my_pipeline')


def make_pipeline():
    """
    Create our pipeline.
    """

    # Base universe set to the Q1500US.

    base_universe = AverageDollarVolume(window_length=20).percentile_between(70, 100)

    latest_close = USEquityPricing.close.latest

    # 14-day RSI
    rsi_14 = RSI(
        inputs=[USEquityPricing.close],
        window_length=14,
        mask=base_universe
    )

    # 20-day, 2 standard deviation Bollinger bands
    bbLow, bbMid, bbHigh = BollingerBands(
        inputs=[USEquityPricing.close],
        window_length=10,
        k=2,
        mask=base_universe
    )

    rsiOverbought = rsi_14 > 70
    rsiOversold = rsi_14 < 30

    bbOverbought = latest_close > bbHigh
    bbOversold = latest_close < bbLow

    overbought = rsiOverbought | bbOverbought
    oversold = rsiOversold | bbOversold

    # Filter to select securities to short.
    shorts = overbought

    # Filter to select securities to long.
    longs = oversold

    # Filter for all securities that we want to trade.
    securities_to_trade = (shorts & longs)

    return Pipeline(
        columns={
            'longs': longs,
            'shorts': shorts
        },
        screen=(securities_to_trade),
    )


def before_trading_start(context, data):
    """
    Get pipeline results.
    """

    # Gets our pipeline output every day.
    pipe_results = pipeline_output(name='my_pipeline')

    # Go long in securities for which the 'longs' value is True,
    # and check if they can be traded.
    context.longs = []
    for sec in pipe_results[pipe_results['longs']].index.tolist():
        if data.can_trade(sec):
            context.longs.append(sec)

    # Go short in securities for which the 'shorts' value is True,
    # and check if they can be traded.
    context.shorts = []
    for sec in pipe_results[pipe_results['shorts']].index.tolist():
        if data.can_trade(sec):
            context.shorts.append(sec)


def my_rebalance(context, data):
    """
    Rebalance daily.
    """

    for security in context.portfolio.positions:
        if security in context.shorts and data.can_trade(security):
            order_target(security, 0)

    if context.longs:
        long_weight = 1.0 / len(context.longs)
        cash = context.portfolio.cash
        for security in context.longs:
            if data.can_trade(security):
                price = data.current(security, 'price')
                shares = math.floor(long_weight * cash / price)
                order_target(security, shares)


def my_record_vars(context, data):
    """
    Record variables at the end of each day.
    """

    longs = shorts = 0
    for position in context.portfolio.positions.items():
        print(position,"\n")
        if position[1].amount > 0:
            longs += 1
        elif position[1].amount < 0:
            shorts += 1

    #env = TradingEnvironment.instance()			

    # Record our variables.
    record(
        leverage=context.account.leverage,
        long_count=longs,
        short_count=shorts
		#benchmark=env.benchmark_returns
    )
	
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