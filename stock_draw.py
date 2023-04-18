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
import stock_select as ss

def stock_draw(code):
    fig, ax = plt.subplots(2,1,figsize=(8, 8))
    df=ss.get_price(code,start_date=ss.past_time,end_date=ss.current_time)
    g1 = sns.lineplot(y='close', x=df.index, data=df,label=code,ax=ax[0]).set(xticklabels=[])
    g2 = sns.lineplot(y='money', x=df.index, data=df,label=code,ax=ax[1]).set(xticklabels=[])
    plt.show()