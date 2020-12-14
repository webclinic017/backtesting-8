# replicate the VIX FIX strategy used in pine script
# originally adapted from source: https://www.tradingview.com/script/TDxSLJRA-Vix-FIX-StochRSI-Strategy/

# Import the backtrader platform
import backtrader as bt, datetime
# import datetime

# not confident in the following equations
# wvf


# Create a Stratey
class vix_fix_stoch_rsi_strategy(bt.Strategy):

    params = dict(
        # stochastic slow inputs
        StochLength = 14, # lookback length of Stochastic")
        StochOverBought = 80, #Stochastic overbought condition")
        StochOverSold = 20, # Stochastic oversold condition")

        # period=3,
        # K, D inputs
        smoothK = 3, # title="smoothing of Stochastic %K ")
        smoothD = 3, # title="moving average of Stochastic %K")



        smoothing_stochastic = 3, #smoothing of Stochastic %K ")


        # Double strategy: RSI strategy + Stochastic strategy
        pd = 22, # LookBack Period Standard Deviation High
        bbl = 20, # Bolinger Band Length
        mult = 2, # Bollinger Band Standard Devaition Up
        lb = 50, # Look Back Period Percentile High
        ph = 0.85, #Highest Percentile - 0.90=90%, 0.95=95%, 0.99=99%
        ltLB = -40, # minval=25, maxval=99, title="Long-Term Look Back Current Bar Has To Close Below This Value OR Medium Term--Default=40")
        mtLB = -14, # minval=10, maxval=20, title="Medium-Term Look Back Current Bar Has To Close Below This Value OR Long Term--Default=14")
        epastr = -3, # minval=1, maxval=9, title="Entry Price Action Strength--Close > X Bars Back---Default=3")
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):

        print('Todays close:')
        print(self.datas[0].close)

        # < Stochastic slow formulas
        stochastic_data = bt.indicators.StochasticSlow(self.datas[0], period=self.p.StochLength)
        k = bt.indicators.SMA(stochastic_data, period=self.p.smoothK)
        d = bt.indicators.SMA(k, period=self.p.smoothD)
        # > end stochastic slow formulas
        
        
        # < Williams Vix Fix Formula
        # highest_close_pd_period = bt.indicators.Highest(self.datas[0].close, period=self.p.pd) ## re-written o nthe next line. this line no longer necessary - cj 12-12-20
        wvf = (  ( bt.indicators.Highest(self.datas[0].close, period=self.p.pd ) - self.datas[0].low )  / ( bt.indicators.Highest(self.datas[0].close, period=self.p.pd) ) )  * 100
        sDev = self.p.mult * bt.indicators.StandardDeviation(wvf, period=self.p.bbl)
        midLine = bt.indicators.SMA(wvf, period=self.p.bbl)
        upperBand = midLine + sDev
        rangeHigh  = ( bt.indicators.Highest(wvf, period=self.p.lb) ) * self.p.ph
        # > End Williams Vix Fix Formula



        # < Filtered Bar Criteria
        upRange_cond_1 = self.datas[0].low > self.datas[0].low.get(ago=-1) 
        upRange_cond_2 = self.datas[0].close > self.datas[0].high.get(ago=-1)
        upRange = bt.And(upRange_cond_1, upRange_cond_2)
        upRange_Aggr = bt.And(self.datas[0].close > self.datas[0].close.get(ago=-1), self.datas[0].close > self.datas[0].open.get(ago=-1))

        # filtered condition
        filtered_cond_1 = bt.Or(wvf.get(ago=-1) >= upperBand.get(ago=-1), wvf.get(ago=-1) >= rangeHigh.get(ago=-1))
        filtered_cond_2 = bt.And(wvf < upperBand, wvf < rangeHigh)        
        filtered = bt.And( filtered_cond_1, filtered_cond_2  )

        # filtered aggressive condition
        filtered_Aggr_cond_1 = bt.Or(wvf.get(ago=-1) >= upperBand.get(ago=-1), wvf.get(ago=-1) >= rangeHigh.get(ago=-1))
        filtered_Aggr_cond_2 = bt.And(1 - wvf < upperBand, wvf < rangeHigh)
        filtered_Aggr = bt.And(filtered_Aggr_cond_1, filtered_Aggr_cond_2)
        # > End Filtered Bar Criteria


        # < Alerts Criteria
        # everything to this point verified translated accurately from pinescript - cj 12-12-20
        alert3_cond1 = self.datas[0].close > self.datas[0].close.get(ago=self.p.epastr)
        alert3_cond2 = bt.Or(  self.datas[0].close < self.datas[0].close.get(ago=self.p.ltLB), self.datas[0].close < self.datas[0].close(ago=self.p.mtLB)  )
        self.alert3 = bt.And(  upRange, alert3_cond1, alert3_cond2, filtered  )

        alert4_cond1 = bt.Or(  self.datas[0].close < self.datas[0].close.get(ago=self.p.ltLB), self.datas[0].close < self.datas[0].close.get(ago=self.p.mtLB)  )
        self.alert4 = bt.And(  upRange_Aggr, self.datas[0].close > self.datas[0].close(ago=self.p.epastr), alert4_cond1, filtered_Aggr  )

        self.isOverBought = bt.And(bt.indicators.CrossOver(k,d), k > self.p.StochOverBought)

        # filteredAlert = alert3

        # aggressiveAlert = alert4

        # if filteredAlert:
        #     self.regularBuy = True

        # if aggressiveAlert:
        #     self.aggressiveBuy = True
        
        # if isOverBought:
        #     self.closePosition = True

        # > End Alerts Criteria

        # To keep track of pending orders
        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)
            self.bars_until_sell = self.bar_executed
            print('bar executed at: ', self.bar_executed)


        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
        
        #if self.bar_executed[0] :
        #    print('original entry: ', self.bar_executed) 
        print('self: ',len(self))
        #print('order: ',self.order)


        if self.alert3:
             self.regularBuy = True

        if self.alert4:
             self.aggressiveBuy = True
        
        if self.isOverBought:
             self.closePosition = True

        if self.position: 
            print('position entry size: ',self.position.size)
            print('position entry price: ',self.position.price)


        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            print('pending.. dont send second')
            return

        # Check if we are in the market
        if not self.position:
            print('not in position')
            print('checking for Regular or Aggressive Buy Conditions..')
            if self.regularBuy:
                print('Regular Buy condition found! Placing buy order..')
                self.buy()
                # BUY, BUY, BUY!!! (with default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = None
                print('+' * 50)

            elif self.aggressiveBuy:
                self.buy()
                # BUY, BUY, BUY!!! (with default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = None
                print('+' * 50)


        else:
            print('in position..')
            # Already in the market ... we might sell
            print('original entry bar: ', self.bar_executed) 
            print('Checking for Sell Conditions..')
            
            if self.closePosition:
                print('Sell condition found! Placing sell order..')
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                # self.order = self.sell()
                # close position may be more efficient than selling position ? .. 12-1-20
                self.order = self.close()
                # SELL, SELL, SELL!!! (with default parameters)
                self.order = None
                print('-' * 50)

