import jqdatasdk as jq
from math import log
import pandas as pd
import numpy as np
import time
import seaborn as sns
import matplotlib.pyplot as plt
import stock_dapan as sd
import stock_each_index as si
import stock_draw as sda
import stock_select as ss
import stock_trade_me as st

#candidate=ss.main()
#for i in candidate['code']:
#    sd.stock_draw(i)
global current_time,past_time,stocks,stop_time
current_time='2021-04-02'
# 对于‘股票近期’这个所考察的时间段的开始时间，为1年前
past_time=str(pd.to_datetime(current_time)-pd.Timedelta(days=365))

# 初始化
stocks=st.initialize()

## 选出股票
candidate=ss.main()

st.trade('000882.XSHE',time='2021-04-02',money=300000)
st.test()
st.situations()
x=1