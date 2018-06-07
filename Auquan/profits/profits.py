
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd



# stocklist=pd.read('~/auquan/capstone/stock_data_new/stocklist.txt')
# print(type(stocklist))
df_outer = pd.read_table('~/auquan/capstone/stocklist', names=('A'))

df = pd.DataFrame(columns= ['stockname', 'avg_profit', 'num_trades'])
for stockname in df_outer['A']:
    df_old = pd.read_csv("~/auquan/capstone/stock_data_new/"+stockname+".csv")
    df_train=df_old[:60000]
    df_train_resampled_10min=df_train[df_train.index%50==0]
    df_train_resampled_10min=df_train_resampled_10min.reset_index(drop=True)   
    df_train_resampled_10min_svwap=df_train_resampled_10min.iloc[:,1]
    df_train_resampled_10min_svwap=df_train_resampled_10min_svwap.to_frame()
    df_train_resampled_10min_svwap=df_train_resampled_10min_svwap.rename(columns={str(list(df_train_resampled_10min_svwap)):0})

    #print stockname
    df_new=pd.DataFrame()

#     df_spread = pd.read_csv("~/auquan/capstone/stock_data_new")
#     df_spread_train=df_spread[:60000]
#     df_spread_train_resampled_10min=df_spread_train[df_spread_train.index%10==0]
#     df_spread_train_resampled_10min=df_spread_train_resampled_10min.reset_index(drop=True)
#     df_spread_train_resampled_10min=df_spread_train_resampled_10min['stockVWAP']
#     df_spread_train_resampled_10min=df_spread_train_resampled_10min.to_frame()

    spread = df_train_resampled_10min.iloc[:,4] - df_train_resampled_10min.iloc[:,3]
    avg_spread = np.mean(spread)
#df_new = pd.DataFrame(data,columns=['Deviations'])
    data = np.array([])
    
    for i in range(6000):

        data= np.append(data,np.mean(df_train_resampled_10min_svwap.iloc[i:i+144])) 
        df_new = pd.DataFrame(data)
#         df_new[i]=np.mean(df_train_resampled_10min.ix[i:i+144,'stockVWAP'])
    df_deviations = df_train_resampled_10min_svwap.iloc[:,0]-df_new.iloc[:,0] - spread - 0.2
    df_deviations_positive = df_deviations[df_deviations>0]
   # df_deviations_positive.dropna(axis = 0)
    dev_mean = np.mean(df_deviations_positive)
    no_of_trades = df_deviations_positive.size
    
    s=pd.Series([stockname, dev_mean, no_of_trades],index= ['stockname', 'avg_profit', 'num_trades'])
    df=df.append(s,ignore_index=True)
    

   # dict={stockname:dev_mean}
#     print(s)
    print(stockname+":"+str(dev_mean)+":"+str(no_of_trades))
df.to_csv("~/auquan/capstone/profits/profits_5d.csv")
    # # df_profit = df_deviations - fees - spread
    # data_maxd
    # for i in range(6000):
    #     data_maxd = np.append

