import pandas as pd
data = pd.read_csv (r'Census_by_Community_2018.csv') 
df = pd.DataFrame(data, columns= ['CLASS','SECTOR','RES_CNT'])

#print(df)
sum1 = df['RES_CNT'].sum()

print("the total =",sum1)

print("-----------------")

groupby_sum1 = df.groupby(['CLASS']).sum()
print(groupby_sum1)

print("-----------------")
groupby_sum1 = df.groupby(['SECTOR']).sum()
print(groupby_sum1)

