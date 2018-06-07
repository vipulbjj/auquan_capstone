import numpy as np
import pandas as pd

df_outer = pd.read_table('~/auquan/capstone/stocklist', names=('A'))

f= open("hurst_scores_1d.txt","w+")
# df_empty = pd.DataFrame()
for stockname in df_outer['A']:
	# df_empty.to_csv("parsedData/"+stockname+".csv")
	with open("stock_data_new/"+stockname+".csv",'w+') as f:
		pass