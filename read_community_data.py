print("--- READING FROM A FILE ---")

def count_else(file_name):
   file = open(file_name)
   count = 0
   for line in open(file_name):
       if "else" in line:
           count +=1
   file.close()
   return count

file_name = "syntax.js"

print(f"number of lines: {len(open(file_name).readlines())}")
print(f"number of characters: {len(open(file_name).read())}")
print(f"number of else's: {count_else(file_name)}")
print(" ")

#display content of a folder
print("--- DISPLAY CONTENT OF A FOLDER ---")

import os
myPath = "C:/EvolveU/python"

all_files = os.listdir(myPath)

for each_item_in_curent_dir in all_files:
   print(f"file name: {each_item_in_curent_dir}, file size: {os.path.getsize(each_item_in_curent_dir)}")
print(" ")

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

# def process_csv (csv_file, key_colomn, value_colomn):
#     with open(csv_file, newline='') as csv_db:
#         reader = csv.reader(csv_db, delimiter =',',)
#         counter = 0
#         dict = {}
#         for row in reader:
#             key = row[int(key_colomn)]
#             value = row[int(value_colomn)]
#             if counter != 0:
#                 if key in dict.keys():
#                     dict[key] =  int(dict[key]) + int(value)
#                 else:
#                     dict[key] = value
#             counter = counter + 1
#         return (dict)


# display_dictionary_line_by_line (process_csv("Census_by_Community_2018.csv", 0, 9))
# display_dictionary_line_by_line (process_csv("Census_by_Community_2018.csv", 4, 9))

print(" ")