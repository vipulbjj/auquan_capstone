
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd

def hurst(input_ts, lags_to_test=24):  
            # interpretation of return value
            # hurst < 0.5 - input_ts is mean reverting
            # hurst = 0.5 - input_ts is effectively random/geometric brownian motion
            # hurst > 0.5 - input_ts is trending
            tau = []
            lagvec = []  
            #  Step through the different lags  
            for lag in range(2, lags_to_test):  
                 #  produce price difference with lag  
                pp = np.subtract(input_ts[lag:], input_ts[:-lag])  
                #  Write the different lags into a vector  
                lagvec.append(lag)  
                #  Calculate the variance of the differnce vector  
                tau.append(np.sqrt(np.std(pp)))  
            #  linear fit to double-log graph (gives power)  
            m = np.polyfit(np.log10(lagvec), np.log10(tau), 1)  
            # calculate hurst  
            hurst = m[0]*2
            return hurst 

# stocklist=pd.read('~/auquan/capstone/stock_data_new/stocklist.txt')
# print(type(stocklist))
df_outer = pd.read_table('~/Auquan/stocklist', names=('A'))

f= open("hurst_scores_2h.txt","w+")
for stockname in df_outer['A']:
    df_old = pd.read_csv("~/Auquan/stock_data_new/"+stockname+".csv")
    df_train=df_old[:60000]
    df_train_resampled_10min=df_train[df_train.index%5==0]
    df_train_resampled_10min.reset_index(drop=True)   
    #print stockname
    
    for i in range(12000):
        df=df_train_resampled_10min[:i]

        hurst_score=hurst(df['stockVWAP'])
	#print(str(i)+":")
        print(i)
	#print(str(i)+":"+str(hurst(df['stockVWAP'])))
        if(i==11999):

              
              f.write(stockname+":"+str(hurst_score))
              f.write('\n')  
f.close()

