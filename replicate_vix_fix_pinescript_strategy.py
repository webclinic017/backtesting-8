# replicate the VIX FIX strategy used in pine script
# originally adapted from source: https://www.tradingview.com/script/TDxSLJRA-Vix-FIX-StochRSI-Strategy/

# Import the backtrader platform # import datetime
import backtrader as bt, datetime



# Create a Strategy
class vix_fix_stoch_rsi_strategy(bt.Strategy):
    #params = dict(
    params = (
        # pyramid buy limit
        #pyramid_limit = 3,
        ('pyramid_limit',2),
        # stochastic slow inputs
        ('StochLength',14), # lookback length of Stochastic")
        ('StochOverBought',80), #Stochastic overbought condition")
        ('StochOverSold',20), # Stochastic oversold condition")

        # period=3,
        # K, D inputs
        ('smoothK',3), # title="smoothing of Stochastic %K ")
        ('smoothD',3), # title="moving average of Stochastic %K")

        ('smoothing_stochastic',3), #smoothing of Stochastic %K ")


        # Double strategy: RSI strategy + Stochastic strategy
        ('pd',22), # LookBack Period Standard Deviation High
        ('bbl',20), # Bolinger Band Length
        ('mult',2), # Bollinger Band Standard Devaition Up
        ('lb',50), # Look Back Period Percentile High
        ('ph',0.85), #Highest Percentile - 0.90=90%, 0.95=95%, 0.99=99%
        ('ltLB',40), # minval=25, maxval=99, title="Long-Term Look Back Current Bar Has To Close Below This Value OR Medium Term--Default=40")
        ('mtLB',-14), # minval=10, maxval=20, title="Medium-Term Look Back Current Bar Has To Close Below This Value OR Long Term--Default=14")
        ('epastr',-3), # minval=1, maxval=9, title="Entry Price Action Strength--Close > X Bars Back---Default=3")
        

        ## OLD DICT PARAMETERS METHOD
        # pyramid buy limit
        # pyramid_limit = 3,
        # # stochastic slow inputs
        # StochLength = 14, # lookback length of Stochastic")
        # StochOverBought = 80, #Stochastic overbought condition")
        # StochOverSold = 20, # Stochastic oversold condition")

        # # period=3,
        # # K, D inputs
        # smoothK = 3, # title="smoothing of Stochastic %K ")
        # smoothD = 3, # title="moving average of Stochastic %K")



        # smoothing_stochastic = 3, #smoothing of Stochastic %K ")


        # # Double strategy: RSI strategy + Stochastic strategy
        # pd = 22, # LookBack Period Standard Deviation High
        # bbl = 20, # Bolinger Band Length
        # mult = 2, # Bollinger Band Standard Devaition Up
        # lb = 50, # Look Back Period Percentile High
        # ph = 0.85, #Highest Percentile - 0.90=90%, 0.95=95%, 0.99=99%
        # ltLB = -40, # minval=25, maxval=99, title="Long-Term Look Back Current Bar Has To Close Below This Value OR Medium Term--Default=40")
        # mtLB = -14, # minval=10, maxval=20, title="Medium-Term Look Back Current Bar Has To Close Below This Value OR Long Term--Default=14")
        # epastr = -3, # minval=1, maxval=9, title="Entry Price Action Strength--Close > X Bars Back---Default=3")
    )

    def log(self, txt, dt=None):
        # ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        # print('%s, %s' % (dt.isoformat(), txt))

    def saveFirstDate(self, txt, dt=None):
        # ''' Logging function for this strategy'''
        print('First run.. saving date to string..')
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
        self.first_date = dt.isoformat()
        self.first_run = False


    def meetsDateRequirements(self, txt, dt=None):
        # ''' Logging function for this strategy'''
        print('First run.. checking date requirements..')
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
        bar_date = dt
        start_requirement_date=datetime.date(2006, 1, 1)
        # print("date passes requirements? ", bar_date < start_requirement_date)
        if not bar_date < start_requirement_date:
            self.first_date_meets_requirements = False
        else: 
            self.first_date_meets_requirements = True


    def __init__(self):

        self.first_date = ''
        self.first_date_meets_requirements = ''

        # date test requirement boolean
        self.first_run = True
        # # Set our desired cash start
        #self.broker.setcash(self.startcash)
        self.startcash = self.broker.getvalue()

        # pyramid order count
        self.pyramid = 0

        # < Stochastic slow formulas
        stochastic_data = bt.indicators.StochasticSlow(self.data, period=self.p.StochLength)
        k = bt.indicators.SMA(stochastic_data, period=self.p.smoothK)
        d = bt.indicators.SMA(k, period=self.p.smoothD)
        # > end stochastic slow formulas
        
        
        # < Williams Vix Fix Formula
        # highest_close_pd_period = bt.indicators.Highest(self.datas[0].close, period=self.p.pd) ## re-written o nthe next line. this line no longer necessary - cj 12-12-20
        wvf = (  ( bt.indicators.Highest(self.data.close(0), period=self.p.pd ) - self.data.low(0) )  / ( bt.indicators.Highest(self.data.close(0), period=self.p.pd) ) )  * 100
        sDev = self.p.mult * bt.indicators.StandardDeviation(wvf, period=self.p.bbl)
        midLine = bt.indicators.SMA(wvf, period=self.p.bbl)
        upperBand = midLine + sDev
        rangeHigh  = ( bt.indicators.Highest(wvf, period=self.p.lb) ) * self.p.ph
        # > End Williams Vix Fix Formula



        # < Filtered Bar Criteria
        upRange_cond_1 = self.data.low(0) > self.data.low(-1) 
        upRange_cond_2 = self.data.close(0) > self.data.high(-1)
        upRange = bt.And(upRange_cond_1, upRange_cond_2)
        upRange_Aggr = bt.And(self.data.close(0) > self.data.close(-1), self.data.close(0) > self.data.open(-1))

        # filtered condition
        filtered_cond_1 = bt.Or(wvf(-1) >= upperBand(-1), wvf(-1) >= rangeHigh(-1))
        filtered_cond_2 = bt.And(wvf < upperBand, wvf < rangeHigh)        
        filtered = bt.And( filtered_cond_1, filtered_cond_2  )

        # filtered aggressive condition
        filtered_Aggr_cond_1 = bt.Or(wvf(-1) >= upperBand(-1), wvf(-1) >= rangeHigh(-1))
        filtered_Aggr_cond_2 = bt.And(1 - wvf < upperBand, wvf < rangeHigh)
        filtered_Aggr = bt.And(filtered_Aggr_cond_1, filtered_Aggr_cond_2)
        # > End Filtered Bar Criteria


        # < Alerts Criteria
        # everything to this point verified translated accurately from pinescript - cj 12-12-20
        alert3_cond1 = self.data.close(0) > self.data.close(self.p.epastr)
        alert3_cond2 = bt.Or(  self.data.close(0) < self.data.close(self.p.ltLB), self.data.close(0) < self.data.close(self.p.mtLB)  )
        # testing idea from backtrader forums
        # self.alert3 = bt.LineNum(float('nan'))
        self.alert3 = bt.And(  upRange, alert3_cond1, alert3_cond2, filtered  )
        #print('alert 3:')
        #print(alert3)

        alert4_cond1 = bt.Or(  self.data.close < self.data.close(self.p.ltLB), self.data.close(0) < self.data.close(self.p.mtLB)  )
        # self.alert4 = bt.LineNum(float('nan'))
        self.alert4 = bt.And(  upRange_Aggr, self.data.close(0) > self.data.close(self.p.epastr), alert4_cond1, filtered_Aggr  )

        # self.isOverBought = bt.LineNum(float('nan'))
        self.isOverBought = bt.And(bt.indicators.CrossOver(k,d), k > self.p.StochOverBought)

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
            # print('bar executed at: ', self.bar_executed)


        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def next(self):
        if self.first_run:
            self.saveFirstDate('Close, %.2f' % self.data.close[0])
            self.meetsDateRequirements('Close, %.2f' % self.data.close[0])
        # print('TOTAL BARS:')
        # print(self.data.buflen())
        # print('END TOTAL BARS')
        # Simply log the closing price of the series from the reference
        # self.firstDateLog('First Date of historical bar:')
        
        self.log('Close, %.2f' % self.data.close[0])
        entry_size = int(5000 / self.data.close[0])
        #self.log('entry share size:')
        #self.log(entry_size)

        
        #if self.bar_executed[0] :
        # print('original entry: ', self.bar_executed) 
        # print('self: ',len(self))
        # print('order: ',self.order)


        # if self.position: 
            # 'position entry size: ',self.position.size)
            # print('position entry price: ',self.position.price)


        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            self.log('pending.. dont send second')
            return

        # Check if we are in the market
        #if not self.position:
        if self.pyramid < self.p.pyramid_limit:
            # print('Pyramid number "' + str(self.pyramid) + '" less than limit. Allowing potential buy..' )
            # keep this print out - old method
            # print('not in position')

            # print('checking for Regular or Aggressive Buy Conditions..')
            if self.alert3:
                self.log('Regular Buy condition found! Placing buy order..')
                self.buy(size=entry_size)
                # BUY, BUY, BUY!!! (with default parameters)
                self.log('BUY CREATE, %.2f' % self.data.close[0])
                self.order = None
                self.pyramid = self.pyramid + 1
                # print('Pyramid number increased by one. Pyramid number now: ' + str(self.pyramid))
                # print('+' * 50)

            elif self.alert4:
                self.buy()
                # BUY, BUY, BUY!!! (with default parameters)
                self.log('BUY CREATE, %.2f' % self.data.close[0])
                self.order = None
                self.pyramid = self.pyramid + 1
                # print('Pyramid number increased by one. Pyramid number now: ' + str(self.pyramid))
                # print('+' * 50)


        elif self.pyramid >= 1:
            # print('Pyramid number "' + str(self.pyramid) + '" MORE than limit. Not allowing buys..' )
            # print('in position..')
            # Already in the market ... we might sell
            # print('original entry bar: ', self.bar_executed) 
            # print('Checking for Sell Conditions..')
            
            if self.isOverBought:
                # print('Sell condition found! Placing sell order..')
                self.log('SELL CREATE, %.2f' % self.data.close[0])
                # self.order = self.sell()
                # close position may be more efficient than selling position ? .. 12-1-20
                self.order = self.close()
                # SELL, SELL, SELL!!! (with default parameters)
                self.order = None
                self.pyramid = 0
                # print('Pyramid number set back to ' + str(self.pyramid))
                # print('-' * 50)


    # def stop(self):
    #     something = 'secret value'
    #     return something
        # current_broker_value = self.broker.getvalue()
        #self.broker.setcash(current_broker_value)
    #     pnl = round(self.broker.getvalue() - self.startcash,2)
    #     print('StochOverSold: {} | Final PnL: {} | Start Cash: {} | End Cash: {}'.format(
    #         self.p.StochOverSold, pnl, self.startcash, self.broker.getvalue()))

