import sys

def printSummary(a,b):
    print ('----- ----- ----- values in first list not in second:')
    q = set (a.keys()) - set(b.keys())
    count = 0 
    for item in q:
        print item
        count +=1 
    print ('----- ----- ----- total ' + str(count))           


    print ('----- ----- ----- values in second list not in first:')
    w = set (b.keys()) - set(a.keys()) 
    count = 0
    for item in w:
        print item 
        count +=1
    print ('----- ----- ----- total ' + str(count))           
    
    # subset of two values
    p = set (a.items()) ^ set(b.items())
            
    # subset unique keys 
    s =  (w | q) 
    

    print '----- ----- ----- Different values: '
    
    # put repeated values in list 
    l = []
    for item in p: 
        if item[0] not in s:
                l.append (item)
    l.sort()
    #print (l)
    
    
    ite = l[0]
    count = 1 
    print (ite[0] ), 
    for item in l:
        if ite[0] != item[0]:
                print ('')
                print (item[0] + ' ' + str(item[1])  ),
                ite = item
                count +=1 
        else:
                print (item[1]),
                
    print (' ')
    print ('----- ----- ----- total ' + str(count))           




def set2dict(aSet):
    tmpDic = {item[0]:item[1] for item in aSet}
    return tmpDic

     
     
def file2dict(fileName):
        d = {}
        with open(fileName) as f:
                for line in f:
                        (key, val) = line.split()
                        d[key] = val
        return d



# a = file2dict("./uno.txt")
# b = file2dict("./two.txt")
# printSummary(a,b)

#a = {'uno':1 , 'dos':2, 'tres':3, 'cuatro':'four', 'cinq':5, 'seis':6, 'siete':7, 'ocho':8}
#b = {'uno':1 , 'dos':2, 'tres':3, 'cuatro':'cua', 'cinco':5, 'seis':6,  'siete':72, 'sietecinco':7.5, 'ocho':8}

# the command to get package list is:   dpkg-query -f '${Package} ${Version}\n' -W


if __name__ == "__main__":
    
    try:
        a = file2dict(sys.argv[1])
        b = file2dict(sys.argv[2])
        printSummary(a,b)
    except: 
        print  ('USAGE: please create two files to compare, use the following command to create a list of packages and versions: ')
        print  ("dpkg-query -f '${Package} ${Version}\n' -W ")
        print (' then provide the two filenames as parameters and the program will provide you with the differences  ')
        print (' for example: python listsDiff.py ./uno.txt ./two.txt  ')
