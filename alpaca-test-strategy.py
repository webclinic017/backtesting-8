import os
from decouple import config
import alpaca_backtrader_api
import sys
import numpy as np
import backtrader as bt
from datetime import datetime

# import strategy/strategies
from replicate_vix_fix_pinescript_strategy import vix_fix_stoch_rsi_strategy


# set alpaca creds
ALPACA_API_KEY = config("ALPACA_API_KEY")
ALPACA_SECRET_KEY = config("ALPACA_SECRET_KEY")

# ALPACA_API_KEY = ''
# ALPACA_SECRET_KEY = ''
ALPACA_PAPER = True

store = alpaca_backtrader_api.AlpacaStore(
    key_id=ALPACA_API_KEY,
    secret_key=ALPACA_SECRET_KEY,
    paper=ALPACA_PAPER
)

if not ALPACA_PAPER:
  broker = store.getbroker()  # or just alpaca_backtrader_api.AlpacaBroker()
  cerebro.setbroker(broker)

######################################################################################################################################################

DataFactory = store.getdata  # or use alpaca_backtrader_api.AlpacaData

data0 = DataFactory(
    dataname='AAPL', 
    historical=True, 
    fromdate=datetime(2014, 1, 1), #timeframe=bt.TimeFrame.Days
    todate = datetime(2019,8,15),
    #bufered = True,
    #compression = 15,
    timeframe = bt.TimeFrame.Days
    )


if __name__ == '__main__':
    #Variable for our starting cash
    startcash = 10000

    #Create an instance of cerebro
    cerebro = bt.Cerebro()

    #Add our strategy
    cerebro.addstrategy(vix_fix_stoch_rsi_strategy)


    #Add the data to Cerebro
    cerebro.adddata(data0)

    # Set our desired cash start
    cerebro.broker.setcash(startcash)

    print(data0)

    # Run over everything
    strats = cerebro.run(maxcpus=1)
