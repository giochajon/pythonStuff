import pandas as pd
#df = pd.read_csv (r'Census_by_Community_2018.csv') 
data = pd.read_csv (r'sample.csv') 

df = pd.DataFrame(data, columns= ['Client Name','Country'])
print (df)

##sum1 = df["res_cnt"].sum()

# groupby_sum1 = df.groupby(['SECTOR']).sum()
# groupby_sum2 = df.groupby(['CLASS']).sum()
##print (sum1)
# print (groupby_sum1)
# print (groupby_sum2)
