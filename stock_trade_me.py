from jqdatasdk import *
import jqdatasdk as jq
from stock_dapan import *
import stock_select as ss
from math import log
import jqdatasdk as jq
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import stock_dapan as sd
import time
import stock_each_index as si
import stock_draw as sda

#账号
#jq.auth('13645798343','932280634Xj')
#jq.auth('19842750844','932280634Xj') 
#jq.auth('18958445859','932280634Xj') 
#jq.auth('18969385969','932280634Xj') 


## 初始化函数，设定要操作的股票、基准等等
def initialize(current_time='2021-04-02'):
    # 设定沪深300作为基准
    global stocks
    stocks=pd.DataFrame(dict(current_money=500000,current_value=0,
                          current_stock='',current_number=0,returnrate=0),
                          index=[current_time])
    # 股票类交易手续费是：买入时佣金万分之1.5，卖出时佣金万分之1.5加千分之一印花税, 每笔交易佣金最低扣5块钱
    close_tax=0.001
    open_tax=0.00115
    min_commission=5
    # 持仓数量
    stocknum = 3 
    # 交易日计时器
    days = 0 
    # 调仓频率
    refresh_rate = 5
    return stocks
    #            current_money  current_value  current_stock  current_number  returnrate
    #2021-04-02         500000              0              0               0           0

## 选出股票
#candidate=ss.main()

#最终购买的股票

candidate=pd.read_csv('D:\杨钦\计算机语言与笔记\quant\数据\购买列表.csv',index_col=0)
#n=len(candidate)
#nrow=int(np.floor(np.sqrt(n))+1)
#ncol=int(np.floor(n/nrow)+1)
#fig, axs = plt.subplots(nrow,ncol)  # .subplots(1,3)
#for i in candidate['code']:
#    sd.stock_draw(i)

#candidate.sort_values(by='alpha')
buylistfinal=candidate['code'].iloc[[3,5,6,12,14,15]]
candidate.loc[buylistfinal].sort_values(by='alpha')
# 000882.XSHE

  
## 交易函数
# amount=股票数,money=花的钱

# trade('000882.XSHE',time='2021-04-02',money=100000,qingcang=False)
def trade(code,time,money,qingcang=False):
    global stocks
    #获取价格
    price=ss.get_price(code,start_date=time,end_date=time,fields=['close']).close[0]
    # 1/4仓建仓
    # 复制上一条数据再进行修改
    stocks.loc[time]=stocks.iloc[-1]
    if qingcang==True:
        # 清仓
        amount=-stocks.loc[time,'current_number']
    else:
        # 普通购买
        amount=np.floor(money/price/100)*100
    try:
        stocks.loc[time,'current_stock']=code
        stocks.loc[time,'current_number']=stocks.loc[time,'current_number']+amount
        stocks.loc[time,'current_money']=stocks.loc[time,'current_money']-amount*price
        #当前市值
        stocks.loc[time,'current_value']=price*stocks.loc[time,'current_number']
        stocks.loc[time,'returnrate']=(stocks.loc[time,'current_money']+stocks.loc[time,'current_value'])/500000-1
    except:
        print('没有钱了')
    return stocks


# 获取交易时间
def tradetime(start_date=ss.current_time,end_date='2021-06-02'):
    dapan=sd.get_index(start_date=start_date,end_date=end_date)
    time=dapan.index.values
    return time 

# 交易策略
# 止盈


def test(start_date=ss.current_time,end_date='2021-06-02'):
    global stoptime
    time=tradetime()
    max=0
    qingcang=0
    # 测试期内的全部数据
    code=stocks.iloc[0]['current_stock']
    price=ss.get_price(code,start_date=start_date,end_date=end_date)

    # currenttime是买入当天
    for i in range(1,len(time)):
        priceclo=price.close[i]
        moneytoday=price.money[i]
        maxi=price.high[i]
        max=np.max([maxi,max])
        #量能
        try:
            moneypre=price.money[i-1]
        except:
            moneypre=price.money[i]
        moneyrate=moneytoday/moneypre
        # 买卖策略
        if (priceclo<max*0.93) and (stocks.loc[time[i-1],'returnrate']>=0):
            #止盈 清仓
            trade(code,time=time[i],money=-stocks.loc[time[i-1],'current_value'],qingcang=True)
            qingcang=1
            stoptime=time[i]
            break
        elif (priceclo<max*0.93) and (stocks.loc[time[i-1],'returnrate']<0) and moneyrate<0.7:
            # 缩量加仓
            trade(code,time=time[i],money=200000)
        elif (priceclo<max*0.93) and (stocks.loc[time[i-1],'returnrate']<0) and moneyrate>1.5:
            #止损 清仓
            qingcang=1
            trade(code,time=time[i],money=-stocks.loc[time[i-1],'current_value'])
            stoptime=time[i]
            break
        elif (priceclo<max*0.93) and (stocks.loc[time[i-1],'returnrate']<0) and moneyrate>1.5:
            #止损 清仓
            qingcang=1
            stoptime=time[i]
            trade(code,time=time[i],money=-stocks.loc[time[i],'current_value'],qingcang=True)
            break
        else:
            trade(code,time=time[i],money=0)
    if qingcang==1:
        print('已清仓，清仓时间：'+stoptime)
        print(stocks)
    else:
        test(start_date=end_date,end_date=str(pd.to_datetime(end_date)+pd.Timedelta(days=40)))

#candidate=ss.main()
#for i in candidate['code']:
#    sd.stock_draw(i)
global current_time,past_time
current_time='2021-04-02'
# 对于‘股票近期’这个所考察的时间段的开始时间，为1年前
past_time=str(pd.to_datetime(current_time)-pd.Timedelta(days=365))
initialize()
trade('000882.XSHE',time='2021-04-02',money=300000)
test()
x=1
# 清仓后继续下一个股票


def situations():
    sns.lineplot(y='returnrate', x=stocks.index, data=stocks,label='code').set(xticklabels=[])
    dapan_test=sd.get_index(start_date=stocks.index.values[0], end_date=stocks.index.values[-1])
    sns.lineplot(y=dapan_test.close/dapan_test.close[0]-1,x=dapan_test.index,data=dapan_test,label='index')
