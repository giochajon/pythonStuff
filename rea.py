import pandas as pd

data = pd.read_excel (r'invoice.xlsx') #(use "r" before the path string to address special character, such as '\'). Don't forget to put the file name at the end of the path + '.xlsx'
print (data)