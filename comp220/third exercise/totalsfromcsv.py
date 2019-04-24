import csv

with open('Census_by_Community_2018.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    classes = []
    sectors = []
    res_cnts = []
    for row in readCSV:
        classe = row[0]
        sector = row[4]
        res_cnt = row[9]
        classes.append(classe)
        sectors.append(sector)
        res_cnts.append(res_cnt)
    uniclasses =  (set(classes))
    unisectors =  (set(sectors))

    print (uniclasses)
