from math import log
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import jqdatasdk as jq
import stock_dapan as dp
import time
import stock_each_index as si
import stock_dapan as sd

#jq.auth('13645798343','932280634Xj')
#jq.auth('19842750844','932280634Xj') 
#jq.auth('18958445859','932280634Xj') 
#jq.auth('18969385969','932280634Xj')


#判断股票是否横盘震荡
## 查看大盘情况



# 大盘指数

#           time         code    close         money
#0    2011-01-04  000001.XSHG  2852.65  1.456598e+11

#current_time = time.strftime('%Y-%m-%d',time.localtime())
#print(pd.to_datetime(current_time)-pd.Timedelta(days=365))
global current_time,past_time
current_time='2021-04-02'
# 对于‘股票近期’这个所考察的时间段的开始时间，为1年前
past_time=str(pd.to_datetime(current_time)-pd.Timedelta(days=365))


# 按市值升序排列
#def query2(stocklist,market_cap1=100):
#    q = jq.query(
#            jq.valuation.code,
#            jq.valuation.market_cap
#            ).filter(
#            jq.valuation.market_cap<market_cap1
#           ).order_by(
#            jq.valuation.market_cap.asc()
#            )
#    l=jq.get_fundamentals(q)
#    return (l[l['code'].isin(stocklist)])
# l
#            code  market_cap
#0    603656.XSHG     20.0033
#1    605298.XSHG     20.0070

#读取全部股票市值
def get_market_cap():
    l=pd.read_csv('D:\杨钦\计算机语言与笔记\quant\数据\股票市值.csv')
    return l

# 用市值筛选股票
def query2(stocklist,marketdata,market_cap1=100):
    l2=marketdata[marketdata['code'].isin(stocklist)]
    return (l2[l2['market_cap']<market_cap1])
#            code  market_cap
#0    603656.XSHG     20.0033
#1    605298.XSHG     20.0070

def get_price(code, start_date='2011-01-01', end_date='2024-12-31',fields=['open','close','high','low','volume','money']):
    l=stock_pool[stock_pool['code']==code]
    #不在股票池里
    if l.empty:
        return None
    else:
        s=l[(l.index>=start_date) & (l.index<=end_date)][fields]
        return s


# 查询符合条件的股票
# fun是判断股票近期状态的函数,如status_stock
def stock_query(fun,stocklist,marketdata,current_time='2021-04-02',fields=['close','money'],marketcap=200):
    dapan=sd.get_index(start_date=past_time, end_date=current_time)
    r_dapan=np.diff(np.log(dapan['close']))
    # 筛选候选股票
    candilist=query2(stocklist,marketdata,market_cap1=marketcap)
    #写成字典，添加Er，夏普ratio等指标
    stock_summary_list=pd.DataFrame(columns=['code','current_price','current_r','expect_r',
                                             'alpha','beta','sigma','VaR_r','CVaR_r','VaR_price','CVaR_price','sharpe_ratio','money','market_cap'])
    for i in candilist['code']:
        # 查询股票数据，可以用本地数据
        stock_r=get_price(i, start_date=past_time, end_date=current_time, fields=fields)
        if stock_r is None:
            continue
        else:
        #stock_r=jq.get_price(i, start_date=past_time, end_date=current_time, fields=fields)
        #            open  close   high   low       volume         money
        #2015-01-05  9.98  10.00  10.17  9.74  458099037.0  4.565388e+09
        # 判断股票近期状态 这里也可以改成先计算各项指标再判断
            #r=np.diff(np.log(stock_r['close']))
            #带入原始数据
            status=fun(stock_r['close'])
            if status==1:
                #得到股票的各项指标
                stock_r=stock_r[~stock_r.index.duplicated()]
                stock_in=si.stock_summary(stock_r['close'],index=i,r_dapan=r_dapan)
                stock_in['code']=i
                stock_in['market_cap']=candilist[candilist['code']==i].market_cap.iloc[0]
                stock_in['money']=stock_r.iloc[-1]['money']
                stock_in['current_price']=stock_r.iloc[-1]['close']
                #合并
                stock_summary_list=pd.concat([stock_summary_list,stock_in],axis=0) 
    return stock_summary_list
# stock_query(status_stock,current_time='2021-04-02')



##############################################
# 判断股票状态
# 1.均线策略
def status_m(data,ma_lag=5,continue_day=10):
    n=len(data)
    ma=[]
    #M(5)
    for i in range(n-ma_lag+1):
        ma.append(np.mean(data[i:i+ma_lag],axis=0))
    #判断是否连续增
    dif=np.diff(ma)
    if all(dif[-continue_day:]>0):    
        status=1    #上升
    elif (all(dif[-continue_day:]<0) or any(dif[-continue_day:]<-0.03)):     
        status=-1   #下跌
    else:
        status=0    #震荡
    return status

def status_baozhang(data,continue_day=10,continue_day2=5):
    #data 是 r
    if (all(data[-continue_day:]>-0.005) or all(data[-continue_day2:]>0)):    
        status=0.5    #上升
    elif (all(data[-continue_day:]<0.005) or any(data[-continue_day:]<-0.03)):     
        status=-1   #下跌
    elif (all(data[-continue_day:-1]<0.02) and all(data[-continue_day:-1]>-0.02) and data[-1]>0.035):     
        status=1   # 横盘暴涨
    else:
        status=0    #震荡
    return status


# 最终的状态判断函数
# 多个status的并
def status_stock(data,ma_lag=5,continue_day=10,continue_day2=5):
    r=np.diff(np.log(data))
    status_ma=status_m(data)
    status_baozhang1=status_baozhang(r)
    if ((status_ma==1 or status_ma==0) and (status_baozhang1==1 or status_baozhang1==0.5)):
        status=1
    else:
        status=0
    return status


#读取股票池
def get_stock_pool():
    stock_pool=pd.read_csv('D:\杨钦\计算机语言与笔记\quant\数据\股票总数据.csv',index_col=0)
    return stock_pool

global stock_pool
stock_pool=pd.read_csv('D:\杨钦\计算机语言与笔记\quant\数据\股票总数据.csv',index_col=0)

def main():
    stocklist=pd.read_csv('D:\杨钦\计算机语言与笔记\quant\数据\股票池.csv',index_col=0).index
    #stock_pool=pd.read_csv('D:\杨钦\计算机语言与笔记\quant\数据\股票总数据.csv',index_col=0)
    l=get_market_cap()
    #buylist=map(stock_query,current_time=[list])
    #buylist=stock_query(status_stock,stocklist,marketdata=l,current_time='2021-04-02')
    buylist=stock_query(status_stock,stocklist,marketdata=l.sort_values('code'),current_time='2021-04-02')
    return buylist

#stock_pool=pd.read_csv('D:\杨钦\计算机语言与笔记\quant\数据\股票总数据.csv',index_col=0)
#list1=main()
#print(list1)

