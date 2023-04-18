import numpy as np
import pandas as pd

# rdata（close and money）
#            open  close   high   low       volume         money
#2015-01-05  9.98  10.00  10.17  9.74  458099037.0  4.565388e+09
#2015-01-06  9.90   9.85  10.23  9.71  346952496.0  3.453446e+09

def stock_summary(rdata,index,r_dapan,rf=0.001):
    r=np.diff(np.log(rdata))
    # 整数索引，所以用iloc'
    current_price=rdata.iloc[-1]
    current_r=r[-1]
    #返回各项指标的df
    er=np.mean(r)
    sigma=np.std(r,ddof=1)
    sharpe_ratio=(er-rf)/sigma
    #beta=np.corrcoef(r,r_dapan)得到相关矩阵
    beta=np.cov(r,r_dapan)[0,1]/np.cov(r,r_dapan)[1,1]
    alpha=er-beta*(er-rf)-rf
    treynor_rate=(er-rf)/beta
    sml_tr=np.mean(r_dapan)-er
    #0.05分位点
    VaR=-np.percentile(r,5)
    CVaR=-np.mean(r[r<-VaR])
    VaR_price=-np.percentile(rdata,5)
    CVaR_price=-np.mean(rdata[rdata<-VaR_price])
    #################量能
    
    stock_summary_list=pd.DataFrame(dict(current_price=current_price,
                                         current_r=current_r,
                                         expect_r=er,alpha=alpha,beta=beta,sigma=sigma,
                                         sharpe_ratio=sharpe_ratio,VaR_r=VaR,CVaR_r=CVaR,
                                         VaR_price=VaR_price,CVaR_price=CVaR_price),index=[index])
    return stock_summary_list
#teststock=pd.read_csv('D:\杨钦\计算机语言与笔记\quant\数据\\teststock.csv',sep=',')
#l=stock_summary(teststock['close'],"000001.XSHE")
#print(l)
#                    code  current_price  market_cap  expect_r  sharpe_ratio         money  current_r     alpha      beta     sigma       VaR      CVaR
#000525.XSHE  000525.XSHE           6.51     64.6981 -0.001343     -0.083257  2.477032e+08  -0.018265 -0.000487  0.365270  0.028141  0.040609  0.057202
#000526.XSHE  000526.XSHE          38.68     22.7164 -0.000095     -0.030949  3.528373e+07   0.001293  0.000277  0.339938  0.035383  0.044780  0.069201