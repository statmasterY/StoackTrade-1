import numpy as np

# 判断股票状态

# 1.均线策略
def status_stock1(data,ma_lag=5,continue_day=10):
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


# 2
# 连续10天ma5大于-5则认为是上升
def status_stock(data,ma_lag=5,continue_day=10,continue_day2=5):
    n=len(data)
    ma=[]
    #MA(5)
    for i in range(n-ma_lag+1):
        ma.append(np.mean(data[i:i+ma_lag],axis=0))
    #判断是否连续增
    dif=np.diff(ma)
    if (all(dif[-continue_day:]>-0.005) or all(dif[-continue_day2:]>0)):    
        status=0.5    #上升
    elif (all(dif[-continue_day:]<0.005) or any(dif[-continue_day:]<-0.03)):     
        status=-1   #下跌
    elif (all(dif[-continue_day:-1]<0.02) and all(dif[-continue_day:-1]>-0.02) and dif[-1]>0.03):     
        status=1   # 横盘暴涨
    else:
        status=0    #震荡
    return status


# 2
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

# 多个status的并
def status_stock(data,ma_lag=5,continue_day=10,continue_day2=5):
    r=np.diff(np.log(data))
    status_ma=status_m(data)
    status_baozhang=status_baozhang(r)
    if ((status_ma==1 or status_ma==0) and (status_baozhang==1 or status_baozhang==0.5)):
        status=1
    else:
        status=0
    return status