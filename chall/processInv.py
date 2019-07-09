import csv
import extract #this is my extract.py file 
import time
import multiprocessing as mp

####################################################
#   This is the main program for the challenge
#   1. Parses the csv (processCurveCsv)
#   2. Processes the file (processLine)
#   3. Creates log upon completion (createSummary)
#   it supports multiprocess paralelism.
####################################################

# process that extracts and places the file (usung multiprocessig)
def processLine(lOrigin,lTargetFile,lBucket,lType,lNoExtB):
   # extract
   resultStat = extract.exWithForce(lOrigin,lTargetFile)
   resultStat.update ({"bucket":lBucket})
   resultStat.update ({"type": lType+" "+lNoExtB })
   output.put(resultStat)

# process to create the summary on succesfull completion 
def createSummary(resultArray): 
     summary: dict = {} # initialize the dictionary to store the stats for buckets
     typeSummary: dict = {}
     
     for resultStat in resultArray:
         #create summary  elements are: 0=compressed Size, 1 uncompressed size
         if  resultStat["bucket"] in summary.keys():
               summary[resultStat["bucket"]][0] += resultStat["compSize"]
               summary[resultStat["bucket"]][1] += resultStat["unCompSize"]
         else:
               summary[resultStat["bucket"]] = []
               summary[resultStat["bucket"]].append (resultStat["compSize"]) 
               summary[resultStat["bucket"]].append (resultStat["unCompSize"])

      # populating sumary by type 
         if  resultStat["type"] in typeSummary.keys():
               typeSummary[resultStat["type"]] += resultStat['numLines']
         else:
               typeSummary[resultStat["type"]] = (resultStat['numLines'])
        
      #printing the summary after the process. 
     
     #print ("-" * 50)
     #print ("Summary for the log processing operation: ")

     #print ("-" * 50)
     print ("")
     for key,val in summary.items():
          print ("")
          print ("Bucket:" + key.capitalize() )
          print( "Total file size of all compressed objects " +str(val[0])  ) 
          print( "Total Bytes decompresed: " + str(val[1])  ) 
   
     print ("")
     print ("Total number of lines in logs, by type:")
     for key,val in typeSummary.items():
          print ("")
          print (key.capitalize() + ": " +str(val)  )
     #print ('==== execution time: '+  str(time.time() - t) + "   ========" ) 


# global variables
#t = time.time() # to calculate execution time (test using the pool)
output = mp.Queue()
processes = []
 


def processCurveCsv():
   try:
         data = csv.DictReader(open("inventory.csv", 'r'))
        
   # remember the order: Bucket, StorageClass, Type (app, database YYYY MM DD), and Date
   # break apart the csv into variables 
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

            # ******* Setup multiprocessing processes
            processes.append (mp.Process(target=processLine, args=(lOrigin,lTargetFile,lBucket,lType,lNoExtB)))

         # Run processes
         for p in processes:
            p.start()
         # gather processes
         for p in processes:
            p.join()
         # Get all process results from the output queue and form array for summary
         results = [output.get() for p in processes]
         createSummary (results)
   except FileNotFoundError:
      print ("Error:could not find inventory.csv file, please place  processInv.py (this file) and extract.py in the same folder as the inventory file. ")


if __name__ == '__main__':
    processCurveCsv()
