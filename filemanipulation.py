#working with CSV files
print("--- WORKING WITH CSV FILES ---")

import csv

def display_dictionary_line_by_line (dict):
   print (' ')
   for item in dict:
       print (item,':', dict[item] )

with open('Census_by_Community_2018.csv', newline='') as census_db:
   reader = csv.reader(census_db, delimiter =',',)
   counter = 0
   dict1 = {}
   dict2 = {}
   for row in reader:
       key1 = row[0]
       key2 = row[4]
       if counter != 0:
           if key1 in dict1.keys():
               dict1[key1] =  int(dict1[key1]) + int(row[9])
           else:
               dict1[row[0]] = row[9]
           if key2 in dict2.keys():
               dict2[key2] =  int(dict2[key2]) + int(row[9])
           else:
               dict2[row[4]] = row[9]
       counter = counter + 1
   display_dictionary_line_by_line (dict1)
   display_dictionary_line_by_line (dict2)
