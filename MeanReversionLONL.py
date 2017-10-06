# -*- coding: utf-8 -*-
"""
Created on Fri Oct  6 12:18:07 2017

@author: amill_000
"""

import numpy as np
import pandas as pd
from quantopian.pipeline import Pipeline
from quantopian.pipeline import CustomFactor
from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.factors import SimpleMovingAverage, AverageDollarVolume
from quantopian.pipeline.data import morningstar
from quantopian.pipeline.filters import Q500US
from quantopian.pipeline.data.quandl import cboe_vix

def rename_col(df):
    df = df.rename(columns={'Close': 'price','Trade Date': 'Date'})
    df = df.fillna(method='ffill')
    df = df[['price', 'Settle','sid']]
    # Shifting data by one day to avoid forward-looking bias
    return df.shift(1)

def initialize(context):
    set_long_only()
    #context.portfolio.starting_cash = 100.00
    #cash = context.portfolio.cash - 900
    
    set_benchmark(sid(8554))
    #orignially these were CLOSE: hours = 5
    schedule_function(ANALYZE,date_rules.every_day(), time_rules.market_open(hours = 2, minutes = 30))
    schedule_function(sell,date_rules.every_day(), time_rules.market_open(hours = 2, minutes = 31))
    schedule_function(buy,date_rules.every_day(), time_rules.market_open(hours = 2, minutes = 32))
    #schedule_function(maximize,date_rules.every_day(), time_rules.market_open(hours = 2, minutes = 33))
    set_slippage(slippage.FixedSlippage(spread=0.0))
    set_commission(commission.PerShare(cost=0, min_trade_cost=0))
    context.nq=5
    context.nq_vol=3
    my_pipe = make_pipeline()
    attach_pipeline(my_pipe, 'my_pipeline')
    context.max_leverage = [0]
    context.ANV = []
    context.buy = []
    context.sell = []
    context.ETN_buy = []
    context.AmountHeldData = []
    context.B = []
    context.S = []
    context.DayCounter = 0.0
    context.L = 1.0
    context.Maximize = True
    my_pipe.add(GetVIX(inputs=[cboe_vix.vix_open]), 'VixOpen')
    context.rv = []
    
        # Front month VIX futures data
    fetch_csv('http://www.quandl.com/api/v1/datasets/CHRIS/CBOE_VX1.csv', 
        date_column='Trade Date', 
        date_format='%Y-%m-%d',
        symbol='v1',
        post_func=rename_col)
    # Second month VIX futures data
    fetch_csv('http://www.quandl.com/api/v1/datasets/CHRIS/CBOE_VX2.csv', 
        date_column='Trade Date', 
        date_format='%Y-%m-%d',
        symbol='v2',
        post_func=rename_col)
    
class GetVIX(CustomFactor):
    window_length = 1
    def compute(self, today, assets, out, vix):
        out[:] = vix[-1]
     
  
    
class Volatility(CustomFactor):  
    inputs = [USEquityPricing.close]
    window_length=132
    
    def compute(self, today, assets, out, close):

        daily_returns = np.log(close[1:-6]) - np.log(close[0:-7])
        out[:] = daily_returns.std(axis = 0)           

class Liquidity(CustomFactor):   
    inputs = [USEquityPricing.volume, morningstar.valuation.shares_outstanding] 
    window_length = 1
    
    def compute(self, today, assets, out, volume, shares):       
        out[:] = volume[-1]/shares[-1]        
        
class Sector(CustomFactor):
    inputs=[morningstar.asset_classification.morningstar_sector_code]
    window_length=1
    
    def compute(self, today, assets, out, sector):
        out[:] = sector[-1]   
        
        
def make_pipeline():
    profitable = morningstar.valuation_ratios.ev_to_ebitda.latest > 0 
    volume = USEquityPricing.volume
    pricing = USEquityPricing.close.latest    
    universe = ( Q500US()&(pricing>0)&(pricing<75)&(volume>1000000)&profitable )
    return Pipeline(screen=universe)

def before_trading_start(context, data):
    context.output = pipeline_output('my_pipeline')
    context.buy = []
    context.sell = []
    context.ETN_buy = []
    context.B = []
    context.S = []
    positions = []
    context.longs = []
    context.v = []
    context.i = []
    for sec in context.portfolio.positions:
        positions.append(sec)
    if len(positions) >= 1:
        context.AmountHeldData.append(len(positions))
    context.vix = context.output["VixOpen"].iloc[0]
    context.rv.append(context.vix)
    context.DayCounter = context.DayCounter + 1
     
    #print('=============================================================================================================' + '\n' )
    
            
def ANALYZE(context, data):
    Universe500=context.output.index.tolist()
    prices = data.history(Universe500,'price',6,'1d')
    daily_rets=np.log(prices/prices.shift(1))
    rets=(prices.iloc[-2] - prices.iloc[0]) / prices.iloc[0]
    # If you don't want to skip the most recent return, however, use .iloc[-1] instead of .iloc[-2]:
    # rets=(prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]
    stdevs=daily_rets.std(axis=0)
    rets_df=pd.DataFrame(rets,columns=['five_day_ret'])
    stdevs_df=pd.DataFrame(stdevs,columns=['stdev_ret'])
    context.output=context.output.join(rets_df,how='outer')
    context.output=context.output.join(stdevs_df,how='outer')    
    context.output['ret_quantile']=pd.qcut(context.output['five_day_ret'],context.nq,labels=False)+1
    context.output['stdev_quantile']=pd.qcut(context.output['stdev_ret'],3,labels=False)+1
    context.longs=context.output[(context.output['ret_quantile']==1) & 
                                (context.output['stdev_quantile']<context.nq_vol)].index.tolist()
    context.shorts=context.output[(context.output['ret_quantile']==context.nq) & 
                                 (context.output['stdev_quantile']<context.nq_vol)].index.tolist()    
#============================================================================================
#REBALANCE
#============================================================================================
    Universe500=context.output.index.tolist()
    context.existing_longs=0
    context.existing_shorts=0
    for security in context.portfolio.positions:
        if security not in Universe500 and data.can_trade(security): 
            order_target_percent(security, 0)
        else:
            if data.can_trade(security):
                current_quantile=context.output['ret_quantile'].loc[security]
                if context.portfolio.positions[security].amount>0:
                    if (current_quantile==1) and (security not in context.longs):
                        context.existing_longs += 1
                    elif (current_quantile>1) and (security not in context.shorts):
                        order_target_percent(security, 0)
                elif context.portfolio.positions[security].amount<0:
                    if (current_quantile==context.nq) and (security not in context.shorts):
                        context.existing_shorts += 1
                    elif (current_quantile<context.nq) and (security not in context.longs):
                        order_target_percent(security, 0)
#============================================================================================
#ANALYZE
#============================================================================================
    spy = [sid(8554)]
    spxs = [sid(37083)]
    Velocity = 0
    #long_leverage = 0
    #short_leverage = 0
    for sec in spy:
        Av = 0
        pri = data.history(spy, "price",200, "1d")
        pos_one = (pri[sec][-3:].mean())
        pos_two = (pri[sec][-15:].mean())
        pos_three = (pri[sec][-165:].mean())
        
        if pos_one < pos_two < pos_three:   
            context.Maximize = False
            context.L = 0.5
            for security in context.longs:
                pri = data.history(context.longs, "price",200, "1d")
                #pos = 'pri[security]'
                pos_one = (pri[security][-1])
                pos_six = (pri[security][-2:].mean())
                #VELOCITY
                velocity_stop = (pos_one - pos_six)
                Velocity = velocity_stop
                if Velocity < 0:
                    context.longs.remove(security)
                else:
                    array = [Velocity, security]
                    context.v.append(array)
        else:
            context.Maximize = True
            context.L = 1.0
            for security in context.longs:
                pri = data.history(context.longs, "price",200, "1d")
                #pos = 'pri[security]'
                pos_one = (pri[security][-1])
                pos_six = (pri[security][-2:].mean())
                #VELOCITY
                velocity_stop = (pos_one - pos_six)
                Velocity = velocity_stop
                if Velocity > 0:
                    context.longs.remove(security)
                else:
                    array = [Velocity, security]
                    context.v.append(array)
    for sec in spy:
        pri = data.history(spy, "price",200, "1d")
        pos_one = (pri[sec][-1])
        pos_six = (pri[sec][-45:].mean())
        Velocity = (pos_one - pos_six)
        
        if Velocity > -0.5:
            #long_leverage = 1.75
            pos_one = (pri[sec][-1])
            pos_six = (pri[sec][-2:].mean())
            #VELOCITY
            velocity_stop = (pos_one - pos_six)
            Velocity = velocity_stop
            if Velocity < -0.5:
                context.longs = []
            if Velocity < -1.0:
                context.longs = []
                for sec in spxs:
                    if data.can_trade(sec) and sec not in context.longs:
                        context.longs.append(sec)
                        array = [Velocity, sec]
                        context.v.append(array)
            elif data.can_trade(sid(37083)):
                for sec in spxs:
                    context.sell.append(sec)
                
        else:
            pos_one = (pri[sec][-1])
            pos_six = (pri[sec][-2:].mean())
            Velocity = (pos_one - pos_six)
            if Velocity < -1.0:
                context.longs = []
                for sec in spxs:
                    if data.can_trade(sec) and sec not in context.longs:
                        context.longs.append(sec)
                        array = [Velocity, sec]
                        context.v.append(array)
            else:
                for sec in spxs:
                    if data.can_trade(sec):
                        context.sell.append(sec)
            
    for sec in context.portfolio.positions:
        if sec not in context.buy:
            context.sell.append(sec)
    
    #if vix is trending up, cut leverage
    #the if statement will rewrite our leverage from calculations above
    pos_1 = (context.rv[-1])
    #if context.DayCounter > 59:
    #    pos_2 = np.mean(context.rv[-60:])
    #    if ((pos_1) > (pos_2)*1.3) :#| (pos_1 < (pos_2)*.9):
    #        context.L = 0.5
    #    else:
    #        context.L = 1.0

    if context.DayCounter > 29:
        pos_2 = np.mean(context.rv[-30:])
        if ((pos_1) > (pos_2)*1.25) :#| (pos_1 < (pos_2)*.9):
            context.L = 0.3
        else:
            context.L = 1.0

    elif context.DayCounter > 9:
        pos_2 = np.mean(context.rv[-10:])
        if ((pos_1) > (pos_2)*1.1) :#| (pos_1 < (pos_2)*.9):
            context.L = 0.45
        else:
            context.L = 1.0
        
    elif context.DayCounter > 4:
        pos_2 = np.mean(context.rv[-5:])
        if ((pos_1) > (pos_2)*1.05) :#| (pos_1 < (pos_2)*.9):
            context.L = 0.6
        else:
            context.L = 1.0
        
    else:
        pos_2 = pos_1
        if ((pos_1) > (pos_2)) :#| (pos_1 < (pos_2)*.9):
            context.L = 0.75
        else:
            context.L = 1.0
        
def sell (context, data):
    for sec in context.sell:
        if data.can_trade(sec) and sec not in context.B:
            order_target_percent(sec, 0)
            context.S.append(sec)            
        
def buy (context, data):
    a = pd.DataFrame(context.v, columns = ["v","sec"])
    a = a.sort_values(["v"], ascending = True)
    print(a)
    context.longs = a["sec"]
    for sec in context.longs:
        if data.can_trade(sec) and sec not in context.portfolio.positions and sec not in context.S and (len(context.longs) > 0):
            #if ( len(context.B) < 40) :
            if ((context.portfolio.cash)) > 0.00 :
                #order_target_percent(sec,((context.portfolio.cash))/50)
                context.B.append(sec)
    print(context.B)
    fa = a[a['sec'].isin(context.B)]
    tw = float(sum(fa['v']))
    for security in context.B:
        w = float(fa['v'][fa['sec']==security])
        try:
            wt = w/tw
        except ZeroDivisionError:
            wt = 1/len(context.B)
        #print(w)
        #print(tw)
        #if tw > 0 :
        if ((context.portfolio.cash)) > 0.00 :
            if wt > 0:
                order_target_value(security,((context.portfolio.cash))*wt*context.L)


def maximize (context, data):  
    if context.Maximize == True:  
        for sec in context.portfolio.positions: 
            if ((context.portfolio.cash)) > 0.0 :
                order_target_value( sec, ((context.portfolio.cash))/len(context.portfolio.positions) )  # try cash/ instead of 100/              
                
             
def handle_data (context, data):
    for sec in context.portfolio.positions:
        if sec not in context.B:
            if context.portfolio.positions[sec].cost_basis * 0.935 > context.portfolio.positions[sec].last_sale_price:
                order_target_percent(sec, 0)
    for s in context.portfolio.positions:
        if context.portfolio.positions[s].amount < 0:
            order_target_percent(s, 0)
    record(VIX=context.vix)
    record(Lever = context.account.leverage)
    
    