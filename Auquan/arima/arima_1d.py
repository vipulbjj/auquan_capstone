# from backtester.trading_system_parameters import TradingSystemParameters
# from backtester.features.feature import Feature
# from datetime import timedelta
# from backtester.dataSource.quant_quest_data_source import QuantQuestDataSource
# # from backtester.timeRule.quant_quest_time_rule import QuantQuestTimeRule
# from backtester.executionSystem.simple_execution_system import SimpleExecutionSystem
# from backtester.orderPlacer.backtesting_order_placer import BacktestingOrderPlacer
# from backtester.trading_system import TradingSystem
# from backtester.version import updateCheck
# from backtester.constants import *
# from backtester.features.feature import Feature
import pandas as pd
import numpy as np
import os
import statsmodels.tsa.arima_model as smt

df_ADANI = pd.read_csv("/home/saumya/Auquan/stock_data_new/ADANIENT.csv")
df_ADANI = df_ADANI.iloc[0:60000]
df_ADANI = df_ADANI[df_ADANI.index%60 == 0]
#predictions = pd.DataFrame(index = df_ADANI.index, columns = stocks)


# step = 12
df_outer = pd.read_table('/home/saumya/Auquan/stocklist_1d', names=('A'))
stocks = df_outer['A']
predictions = pd.DataFrame(index = df_ADANI.index, columns = stocks.values)
predictions = predictions.reset_index(drop = True)
temp = 0
predictions_all=None
check_empty=1
# predictions = pd.DataFrame(columns = )
for stockname in df_outer['A']:    
                    df = pd.read_csv("/home/saumya/Auquan/stock_data_new/"+stockname+".csv")
                    rng = pd.date_range('2017-01-02 09:16:00', periods=1000, freq='60min')
                    df = df.iloc[0:60000]
                    df = df[df.index%60 == 0]
                    df_new = pd.DataFrame(df['stockVWAP'], index = rng)
                    df_new['stockVWAP'] = df['stockVWAP'].values
                    df_new = df_new.dropna()
                    for k in range(1000):
    #                     df_scan = df.iloc[0:k, 1]
                        # df = pd.DataFrame(data, index = ratio_1.index)
                        #print(i)
                        #print("TEST")
                        df_scan = df_new.iloc[:k]
                        best_aic = np.inf
                        best_order = None
                        best_mdl = None
                        #print(test[sym][-1])
                        pq_rng = range(4) # [0,1,2,3]
                        d_rng = range(2) # [0,1]
                        #train.dropna(inplace= True)
                        for i in pq_rng:
                            for d in d_rng:
                                for j in pq_rng:
    #                                   if(k>10):  
                                    try:
    #                                     print("no error")
                                        tmp_mdl = smt.ARIMA(df_scan, order=(i,d,j)).fit(method='mle', trend='nc', disp = 0)
                                        #print(tmp_mdl.aic)
                                        tmp_aic = tmp_mdl.aic;
                                        #print(tmp_aic)
                                        if tmp_aic < best_aic:
                                            best_aic = tmp_aic
                                            best_order = (i, d, j)
                                            best_mdl = tmp_mdl
                                    except:continue

                                      
                                    
                        #print(best_mdl)                         
                        if best_mdl is None:                                 
                                    #print("bakwas")
                                    temp = temp + 1                         
                        else:

                                    #print(k)
                                    predict = best_mdl.forecast(steps = 24, alpha = 0.01)[0]
                                    mean = np.mean(predict)
                                    threshold = np.std(predict)
                                    if(df_scan.iloc[k - 1, 0] > mean + threshold):
                                            # print("IF ------- IF")  
                                            predictions.loc[[k], [stockname]] = 0
                                    elif(df_scan.iloc[k - 1, 0] < mean - threshold):
                                            predictions.loc[[k], [stockname]] = 1 
                                    else:
                                            predictions.loc[[k], [stockname]] = 0.5        
                                            # print("ELSE ------- ELSE")
                                            # print(predictions.loc[[k], [stockname]])
                                    # predictions.to_csv("predictions.csv") 
                    predictions_single = predictions.values
                        #predictions_write = predictions.values
                        #np.concatenate([predictions_all,predictions_write])
                    if check_empty==1:
                                    
                                    predictions_all=predictions_single
                                    check_empty=0

                    else:
                                    predictions_all=np.concatenate([predictions_all,predictions_single])

predictions_new = pd.DataFrame(data=predictions_all, columns = stocks.values)

predictions_new.to_csv("predictions_new.csv")  

# predictions.to_csv("predictions.csv")

#                                     else: 
#                                         (predict[-1] <= (ma_10.iloc[-1, k] - 2*sdev_90.iloc[-1,0])):
#                                         predictions[PAIRIDS[k+1][0]] = 0
#                                         predictions[PAIRIDS[k+1][1]] = 1