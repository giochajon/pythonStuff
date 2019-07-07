import csv
import extract
import time
from multiprocessing import Process

t = time.time() # to calculate execution time (test using the pool)
data = csv.DictReader(open("inventory.csv", 'r'))

# remember the order: Bucket, StorageClass, Type (app, database YYYY MM DD), and Date 

summary: dict = {} # initialize the dictionary to store the stats for buckets
typeSummary: dict = {}

for row in data:

   lBucket = row ['Bucket']
   lStorageClass = row ['StorageClass']
   lOrigin = "./remoteobjects/"+lBucket +"/"+ row['Key']
   lKey = row['Key'].split("/")
   lType = lKey[3]
   lYear = lKey[0]
   lMonth = lKey[1]
   lDay = lKey[2]
   lDirName = "./processedobjects/" +lBucket +"/"+lStorageClass+"/"+lType+"/"+lYear+"/"+lMonth+"/"+lDay+"/"
   lNoExt = ".".join(lKey[-1].split(".")[0:-1])  # remove everyting after the last dot in the filename
   lNoExtB = "".join(lKey[-1].split(".")[0]) # subtype of log error / reques / query


   lTargetFile = lDirName + lNoExt

   #print (lOrigin,lTargetFile) # test to verify that the passed arguments are correct 
    
   # extract
   resultStat = extract.exWithForce(lOrigin,lTargetFile)   
   print("read compressed "+ str(resultStat["compSize"])+  " bytes, wrote "+ str(resultStat['unCompSize']) + " bytes from file, number of lines: "+ str(resultStat['numLines']))

   #create summary  elements are: 0=compressed Size, 1 uncompressed size, 2 Number of lines 
   if  lBucket in summary.keys():
        summary[lBucket][0] += resultStat["compSize"]
        summary[lBucket][1] += resultStat["unCompSize"]
        #summary[lBucket][2] +=resultStat['numLines']
   else:
        summary[lBucket] = []
        summary[lBucket].append (resultStat["compSize"]) 
        summary[lBucket].append (resultStat["unCompSize"])
        #summary[lBucket].append (resultStat['numLines'])

     # populating sumary by type 
   if  lType +" "+lNoExtB in typeSummary.keys():
        typeSummary[lType +" "+lNoExtB] += resultStat['numLines']
   else:
        typeSummary[lType +" "+lNoExtB] = (resultStat['numLines'])
        
# printing the summary after the process. 
  
print ("-" * 50)
print ("Summary for the log processing operation: ")

print ("-" * 50)
for key,val in summary.items():
    print ("-\t Bucket:" +key )
    print( "-\t Total Bytes in compressed files: " +str(val[0])  ) 
    print( "-\t Total Bytes decompresed: " + str(val[1])  ) 
    #print( "-\t Number of lines: "   +str(val[2])  )
    print ("-" * 50)

print ("." * 50)
print (".   Number of Lines by type:")
print ("." * 50)
for key,val in typeSummary.items():
     print (".\t "+key + ": " +str(val)  )
print ("." * 50)


print ('==== execution time: '+  str(time.time() - t) + "   =========" ) 
