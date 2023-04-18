from math import log
from jqdatasdk import *
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
sns.set_theme(style="darkgrid")
import jqdatasdk as jq
#jq.auth('13645798343','932280634Xj') 

## 查看大盘情况

# 经验分布函数
class ECDF:
    def __init__(self, observations):
        # 初始化函数，储存所有样本
        self.observations = observations
    def __call__(self, x):
        counter = 0
        for obs in self.observations:
            # 如果样本中观测值小于或者等于x，则记为1
            if obs <= x:
                counter += 1
        return counter / len(self.observations)

# 大盘指数
# 列表才有time列
def get_index(index_name=['000001.XSHG'],start_date='2011-01-01', end_date='2200-01-01', frequency='daily',fields=['close','money']):
    l=pd.read_csv('D:\杨钦\计算机语言与笔记\quant\数据\dapan.csv',index_col=0)
    dapan=l[(l.index>=start_date) & (l.index<=end_date)][fields]
    #dapan=jq.get_price(index_name, start_date=start_date, end_date=end_date, frequency=frequency, fields=fields)
    return dapan
#dapan=get_index()
#           time         code    close         money
#0    2011-01-04  000001.XSHG  2852.65  1.456598e+11


#绘制折线图
#sns.lineplot(data=df,x='time',y='close')
#plt.show()

#大盘位置分位点，作为风险估计
def quantile_index(x,data):
    #拟合经验分布函数
    F=ECDF(data)
    #下分位点，越小说明位置越低
    return F(x)


#判断数据上升，下跌还是震荡
# 连续10天ma5大于-5则认为是上升
# data=dapan_recent
def status(data,ma_lag=5,continue_day=10):
    n=len(data)
    ma=[]
    #MA(5)
    for i in range(n-ma_lag+1):
        ma.append(np.mean(data[i:i+ma_lag],axis=0))
    #判断是否连续增
    dif=np.diff(ma)
    if all(dif[-continue_day:]>-5):    
        status=1    #上升
    elif (all(dif[-continue_day:]<0) or any(dif[-continue_day:]<-10)):     
        status=-1   #下跌
    else:
        status=0    #震荡
    return status


#主程序
def main(current_time,target_index='close',daysback=100,continue_day=10,ma_lag=5):
    current_index=current_time
    #获取大盘数据
    dapan=get_index(start_date='2011-01-01', end_date='2020-12-31') #local
    dapan_recent=get_index(end_date=current_time)[-daysback:]       #recent 100 days
    # close data
    df=dapan[target_index]
    df_recent=dapan_recent[target_index]
    current_index=df_recent.iloc[-1]
    lag1_index=dapan_recent[target_index].iloc[-2]

    #量能
    dapan_mon=get_index(end_date=current_time)['money'][-256:] 
    dapan_mon_cur=dapan_recent['money'].iloc[-1] 

    #log-return
    r=np.diff(np.log(df))
    r_recent=np.diff(np.log(df_recent))
    current_r=np.log(current_index)-np.log(lag1_index)

    #总的历史分位点
    q_index=quantile_index(current_index,df)
    q_r=quantile_index(current_r,r)
    q_r_recent=quantile_index(current_r,r_recent)
    q_mon=quantile_index(dapan_mon_cur,dapan_mon)

    #大盘的标准差
    sigma_r=r.std()
    sigma_r_rec=r_recent.std()

    #判断大盘上升，下跌还是震荡
    status_dapan=status(dapan_recent,continue_day=continue_day,ma_lag=ma_lag)

    res=pd.DataFrame(dict(current_time=current_time,current_index=current_index,
                          q_index=q_index,q_r=q_r,q_r_recent=q_r_recent,q_mon_recent=q_mon,
                          sigma_r=sigma_r,sigma_r_rec=sigma_r_rec,status_dapan=status_dapan),
                          index=[current_time])
    #           current_time  current_index   q_index       q_r  q_r_recent  q_mon_recent   sigma_r  sigma_r_rec  status_dapan
    #2021-04-02   2021-04-02        3484.39  0.936678  0.718223    0.646465        0.4375  0.013501     0.010299             1
    return res