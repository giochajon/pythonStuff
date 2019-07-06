import csv
import extract


data = csv.DictReader(open("inventory.csv", 'r'))

# remember the order: Bucket, StorageClass, Type (app, database YYYY MM DD), and Date 

a=0

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
   
   lTargetFile = lDirName + lNoExt


   #print("Expected path:" + lDirName    ) 
   
   #print (lOrigin,lTargetFile)
   
   # extract
   extract.exWithForce(lOrigin,lTargetFile)   
   

   a += 1 
   if a == 2:
       break
