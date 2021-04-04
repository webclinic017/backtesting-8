import os
import matplotlib
from decouple import config
import alpaca_backtrader_api
import sys
import numpy as np
import backtrader as bt
from backtrader import Analyzer
from backtrader.utils import AutoOrderedDict, AutoDict
from datetime import datetime,date,timedelta
import time
import csv
import requests
import json
from extensions.analyzers import BasicTradeStats2
from get_secret import get_secret

## 
# import strategy/strategies
from replicate_vix_fix_pinescript_strategy import vix_fix_stoch_rsi_strategy
# from vix_fix_simplified import vix_fix_stoch_rsi_strategy




def backtrader_minimal_test():
    # get todays date
    today = date.today()
    date_time_formatted = today.strftime("%m_%d_%y")
    # get current timestamp rounded to interval (nearest whole number)
    ts = str(int(time.time()))


    # set alpaca creds
    ALPACA_API_KEY=get_secret('ALPACA_API_KEY')
    ALPACA_SECRET_KEY=get_secret('ALPACA_SECRET_KEY')
    ALPACA_API_LIVE_KEY=get_secret('ALPACA_API_LIVE_KEY')
    ALPACA_API_LIVE_SECRET_KEY=get_secret('ALPACA_API_LIVE_SECRET_KEY')
    TELEGRAM_BOT_STOCK_UPDATE_KEY=get_secret('TELEGRAM_BOT_STOCK_UPDATE_KEY')


    # env method - use aws secrets instead
    # ALPACA_API_KEY = config("ALPACA_API_KEY")
    # ALPACA_SECRET_KEY = config("ALPACA_SECRET_KEY")
    # ALPACA_API_LIVE_KEY = config("ALPACA_API_LIVE_KEY")
    # ALPACA_API_LIVE_SECRET_KEY = config("ALPACA_API_LIVE_SECRET_KEY")


    ALPACA_PAPER = True

    store = alpaca_backtrader_api.AlpacaStore(
        key_id=ALPACA_API_KEY,
        secret_key=ALPACA_SECRET_KEY,
        paper=ALPACA_PAPER,
        # use polygon data since alpaca seems to only go back as far as 04-15-2008
        usePolygon= False
    )

    if not ALPACA_PAPER:
        broker = store.getbroker()  # or just alpaca_backtrader_api.AlpacaBroker()
        cerebro.setbroker(broker)

    # alter plot output for serverless (headless) displays
    def saveplots(cerebro, numfigs=1, iplot=True, start=None, end=None,
                width=16, height=9, dpi=300, tight=True, use=None, file_path = '', **kwargs):

            from backtrader import plot
            if cerebro.p.oldsync:
                plotter = plot.Plot_OldSync(**kwargs)
            else:
                plotter = plot.Plot(**kwargs)

            figs = []
            for stratlist in cerebro.runstrats:
                for si, strat in enumerate(stratlist):
                    rfig = plotter.plot(strat, figid=si * 100,
                                        numfigs=numfigs, iplot=iplot,
                                        start=start, end=end, use=use)
                    figs.append(rfig)

            for fig in figs:
                for f in fig:
                    f.savefig(file_path, bbox_inches='tight')
            return figs

    # telegram photo upload function
    def send_photo(chat_id, file_opened):
        method = "sendPhoto"
        params = {'chat_id': chat_id}
        files = {'photo': file_opened}
        send_photo_url_1='https://api.telegram.org/bot'+TELEGRAM_BOT_STOCK_UPDATE_KEY+'/'
        resp = requests.post(send_photo_url_1 + method, params, files=files)
        return resp


        ############################################################ Add analyzers

    def printTradeAnalysis(analyzer, pyramid_limit):
        '''
        Function to print the Technical Analysis results in a nice format.
        '''
        #Get the results we are interested in
        total_open = analyzer.total.open
        total_closed = analyzer.total.closed
        total_won = analyzer.won.total
        total_lost = analyzer.lost.total
        win_streak = analyzer.streak.won.longest
        lose_streak = analyzer.streak.lost.longest
        pnl_net = round(analyzer.pnl.net.total,2)
        starting_value = 20000
        ending_value = starting_value + pnl_net
        strike_rate = round((total_won / total_closed) * 100, 2)

        #Designate the rows
        r1 = [ ending_value, starting_value, total_open, total_closed, total_won, total_lost, strike_rate, win_streak, lose_streak, pnl_net, pyramid_limit ]
        
        return r1


    # delete me - no longer needed
    def printSQN(analyzer):
        sqn = round(analyzer.sqn,2)
        # print('SQN: {}'.format(sqn))
        return sqn

    def printBasicTradeStats2(analyzer):
        print('Basic Trade Stats 2: {}'.format(analyzer.BasicTradeStats2))

    def printDrawdown(analyzer):
        drawDownToPrint = round(analyzer.max.drawdown,2)
        # print('Drawdown : {}'.format(drawDownToPrint))
        return drawDownToPrint

    def testSymbolAlpacaExists(symbol_to_lookup_on_alpaca):
        URL = 'https://api.alpaca.markets/v2/assets/'+symbol_to_lookup_on_alpaca
        HEADERS = {
            "APCA-API-KEY-ID": ALPACA_API_KEY,
            "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY
        }
        # print('Headers: '+str(HEADERS))
        r = requests.get(timeout = 5, url = URL, headers={'APCA-API-KEY-ID': ALPACA_API_LIVE_KEY, 'APCA-API-SECRET-KEY': ALPACA_API_LIVE_SECRET_KEY })
        
        return str(r.status_code)




    ############################################################ End Add analyzers






    ############################################################# Main Script

    #if __name__ == '__main__':
    #Variable for our starting cash
    import logging
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    # date work
    today_date=datetime.today().strftime('%Y-%m-%d')
    yesterday_date = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')

    # symbols = ['EW']
    # prod symbols (35 in total)
    symbols = ["ATO",	"HTLF",	"MKC.V",	"EW",	"ATR",	"LAUR",	"ROL",	"FCNCA",	"ATRI",	"KAI",	"NPK",	"RSG",	"PEG",	"EXPO",	"HTLF",	"BANFP",	"HON",	"ROL",	"GILD",	"PEG",	"DGX",	"MLAB",	"ICAD",	"QQQ",	"CASY",	"AFG",	"LEG",	"ERIE",	"CVCO",	"FCNCA",	"MGP",	"RDY",	"RSG",	"LMNX",	"AJG"]
    # test symbols
    # symbols = ["PUI", "NXTG", "PNQI", "QTEC", "CCI"	]

    header_written = 0

    for symbol_to_check in symbols:
        # reset these values at the top of each loop
        first_date_recorded = ''
        first_date_recorded_meets_requirements = ''
        # first check to see if symbol exists on alpaca. Otherwise, no reason to backtest it
        check_for_success = testSymbolAlpacaExists(symbol_to_check)
        if check_for_success != '200':                
            print('Error! Did not find symbol: '+symbol_to_check+ ' in Alpaca. ('+check_for_success +') Will not backtest.')
            continue 
        #Create an instance of cerebro
        cerebro = bt.Cerebro(optreturn=False)

        # $20k
        startcash = 20000

        DataFactory = store.getdata  # or use alpaca_backtrader_api.AlpacaData


        data0 = DataFactory( 
        dataname=symbol_to_check,
        historical=True, 
        fromdate=datetime(1995, 1, 1), #timeframe=bt.TimeFrame.Days
        todate = datetime(2021,3,10),
        # buffered = True,
        #compression = 15,
        timeframe = bt.TimeFrame.Days
        )

        print('Processing data for symbol: '+symbol_to_check)
        

        # Set our desired cash start
        cerebro.broker.setcash(startcash)



        #############################################################################  Add our strategy

        # for optimization of parameters
        # cerebro.optstrategy(vix_fix_stoch_rsi_strategy, pyramid_limit=range(1,3))
        cerebro.optstrategy(vix_fix_stoch_rsi_strategy)
        # cerebro.addstrategy(vix_fix_stoch_rsi_strategy)

        #############################################################################  END Add our strategy



        #Add the data to Cerebro
        cerebro.adddata(data0)

        # Add the analyzers we are interested in
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
        cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
        cerebro.addanalyzer(BasicTradeStats2, _name="BasicTradeStats2")



        # Run over everything
        opt_runs = cerebro.run(maxcpus=1, runonce=False)
        # firstStrat = opt_runs[0]

        # optimization test result work
        # Generate results list
        final_results_list = []
        for run in opt_runs:
            for strategy in run:
                # print(strategy.strategy_test_value)
                first_date_recorded = str(strategy.first_date)
                first_date_recorded_meets_requirements = strategy.first_date_meets_requirements
                latest_buy_date = str(strategy.latest_buy_date)
                print('YESTERDAY DATE:')
                print(yesterday_date)
                print('TODAY DATE:')
                print(today_date)
                print('LATEST BUY DATE:')
                print(latest_buy_date)
                print('END LATEST BUY DATE.')
                buy_message=(latest_buy_date == yesterday_date) or (latest_buy_date == today_date)
                # buy_message=True
                if buy_message:
                    print('!Found a buy for today or yesterday for symbol: '+symbol_to_check)
                else:
                    print('Did not find a buy signal for today or yesterday for symbol: '+symbol_to_check+'. Proceeding to check next symbol..')
                    continue
                total_strategy_bars = str(strategy.data.buflen())

                trade_print_analysis = printTradeAnalysis(strategy.analyzers.ta.get_analysis(), strategy.p.pyramid_limit)
                trade_print_sqn = printSQN(strategy.analyzers.sqn.get_analysis())
                trade_print_drawdown = printDrawdown(strategy.analyzers.drawdown.get_analysis())
                print('PROFIT FACTOR')
                print(strategy.analyzers.BasicTradeStats2.rets.all.stats.profitFactor) 
                print(strategy.analyzers.BasicTradeStats2.print())
                # stats from basictradestats2

                # kelly - Kelly % - the optimal percentage (in hindsight) to have risked on your system per trade -> to make the maximum amount of profit.
                kelly_percent = strategy.analyzers.BasicTradeStats2.rets.all.stats.kellyPercent

                # expectancy - Expectancy % - this is the expectancy from system. e.g. for every unit risked what % can you expect to make. e.g. 28.7% means for every $1 you risked, your return was 28.7 cents.
                expectancy_percent = strategy.analyzers.BasicTradeStats2.rets.all.stats.expectancyPercentEstimated

                # reward risk - from site: also called Risk Reward Ratio = average win / average loss
                reward_risk_ratio =  strategy.analyzers.BasicTradeStats2.rets.all.stats.rewardRiskRatio

                # trades per year
                trades_per_year = strategy.analyzers.BasicTradeStats2.rets.all.stats.tradesPerYear

                # profit factor
                profit_factor = strategy.analyzers.BasicTradeStats2.rets.all.stats.profitFactor

                # profit - profit average
                average_pnl = strategy.analyzers.BasicTradeStats2.rets.all.pnl.average
                print(strategy.analyzers.BasicTradeStats2.rets.all.stats.profitFactor)
                # trades per year


                array_item_to_add = [ symbol_to_check, trade_print_analysis[0], trade_print_analysis[1], trade_print_analysis[2], trade_print_analysis[3], trade_print_analysis[4], trade_print_analysis[5], trade_print_analysis[6], trade_print_analysis[7], trade_print_analysis[8], trade_print_analysis[9], trade_print_sqn, trade_print_drawdown, trade_print_analysis[10], total_strategy_bars, first_date_recorded, first_date_recorded_meets_requirements, kelly_percent, expectancy_percent, reward_risk_ratio, trades_per_year, profit_factor, average_pnl  ]
                final_results_list.append(array_item_to_add)
                # final_results_list.append(trade_print_sqn)
                # final_results_list.append(trade_print_drawdown)

        # symbol_to_check[1], trade_print_analysis[0], trade_print_analysis[1], trade_print_analysis[2], trade_print_analysis[3],  trade_print_analysis[4], trade_print_analysis[5], trade_print_analysis[6], trade_print_analysis[7], trade_print_analysis[8], trade_print_analysis[9], trade_print_sqn, trade_print_drawdown, trade_print_analysis[10], total_strategy_bars, first_date_recorded, first_date_recorded_meets_requirements,   kelly_percent,   expectancy_percent,   reward_risk_ratio,   trades_per_year,    profit_factor,   average_pnl 
        #'Symbol',           'Ending Value',          'Starting Value',        'Positions Still Open',  'Total Positions Closed', 'Total Won',             'Total Lost',            'Strike Rate',           'Win Streak',            'Lose Streak',           'Net Profit or Loss',    'SQN Score',     'Max Drawdown %',     'Pyramid Limit',          'Total Bars',       'First Date Recorded','First Date Recorded Meets Requirements'  'Kelly Percent', 'Expectancy Percent', 'Reward Risk Ratio', 'Trades Per Year', 'Profit Factor', 'Average pnl' 



        #Sort Results List
        # by_period = sorted(final_results_list, key=lambda x: x[0])
        by_ending_value = sorted(final_results_list, key=lambda x: x[0], reverse=True)

        print("Trade Analysis Results ordered by Ending Value (also includes total open):")
        # csv 
        # r1 = [ ending_value, starting_value, total_open, total_closed, total_won, total_lost, strike_rate, win_streak, lose_streak, pnl_net, pyramid_limit ]

        # array_item_to_add = [ trade_print_analysis[7], trade_print_analysis[8], trade_print_analysis[9], trade_print_sqn, trade_print_drawdown, trade_print_analysis[10]]
        

        
        if buy_message:
            for result in by_ending_value:
                print(result)
                print('Ending value: ' + str(result[0]) + ' Starting Value: ' + str(result[1]) + ' Total Open: ' + str(result[2]) +' Total Closed: ' + str(result[3]) + ' Total Won: ' + str(result[4]) + ' Total Lost: ' + str(result[5]) + ' Strike Rate: ' + str(result[6]) + ' Win Streak: ' + str(result[7]) + ' Lose Streak: ' + str(result[8]) + ' PnL Net: ' + str(result[9]) + ' SQN: ' + str(result[10]) + ' Drawdown(%): ' + str(result[11]) + ' INDICATORS: '+' Pyramid Limit: ' + str(result[12]) + 'TOTAL BARS' + str(result[13]))
                # write the data rows to csv  
                    

            #Get final portfolio Value
            portvalue = cerebro.broker.getvalue()

            #Print out the final result
            print('Final Portfolio Value: ${}'.format(portvalue))

            # wont run in vs code terminal. must be run in standalone terminal in linux, due to issues with plotting requirements
            # cerebro.plot(style='candlestick')
            #alternative way to save but still generates preview window
            # figure = cerebro.plot(style='candlestick')[0][0]
            # figure.savefig('example3.png')

            saveplots(cerebro, file_path = '/tmp/savefig.png') #run it

            # now send the output via telegram for a mobile alert
            telegram_message_body='Final Portfolio Value: ${}'.format(portvalue)
            telegram_chat_id='287105715'
            send_message_url='https://api.telegram.org/bot'+TELEGRAM_BOT_STOCK_UPDATE_KEY+'/sendMessage?chat_id='+telegram_chat_id+'&text='+telegram_message_body
            # send_photo_url='https://api.telegram.org/bot'+TELEGRAM_BOT_STOCK_UPDATE_KEY+'/sendPhoto?chat_id='+telegram_chat_id+'&photo=@'+'savefig.jpg' #'photo':

            requests.post(url = send_message_url)

            output=send_photo(telegram_chat_id, open('/tmp/savefig.png', 'rb'))
            print(output)
    if buy_message == False:
        telegram_message_body='No buy signals found'
        telegram_chat_id='287105715'
        send_message_url='https://api.telegram.org/bot'+TELEGRAM_BOT_STOCK_UPDATE_KEY+'/sendMessage?chat_id='+telegram_chat_id+'&text='+telegram_message_body

        requests.post(url = send_message_url)
            







 
    

    
 
        

        

