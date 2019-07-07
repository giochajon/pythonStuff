import bz2
import gzip
import shutil
import sys
import os
import binascii 

#################################
#  extract with force will extract a source file into a target
#  the target path will be forced to be created
#  used by processInv.py to extract one logfiles 
#  tested to work from command line as well
#  
#################################

def exWithForce(source,target):
     
  a = target.split("/")
  targetDir = "/".join (a[0:-1])
  cSiz = os.stat(source).st_size # this var has compressed size 

# Create target directory & all intermediate directories if don't exists
  try:     
    if not os.path.exists(targetDir):
      os.makedirs(targetDir,exist_ok=True)
  except OSError as err:
        print(err)
        pass    
      
  else:    
    #print("Directory " , targetDir ,  " already exists") 
    pass # quiet please


    #extract
  if  whichComp(source) == "gz": # test gz file
      #target = target[0:-3] # .gz
      f = gzip.open(source)
      data = f.read()
      if os.path.exists(target):
         os.remove(target)
      fd = os.open( target, os.O_RDWR|os.O_CREAT )
      uRet = os.write(fd,data) # this variable has the size in bytes for the uncompressed file, we need to return
      nLines = len(data.splitlines()) # save the number of lines before closing file, we need to return
      
      os.close(fd)
      

  elif  whichComp(source) == "bz2": # is a bz2 file
      #target = target[0:-4]
      f = bz2.open(source)
      data = f.read()
      if os.path.exists(target):
         os.remove(target)
      fd = os.open( target, os.O_RDWR|os.O_CREAT )
      uRet = os.write(fd,data) # this variable has the size in bytes for the uncompressed file, we need to return 
      nLines = len(data.splitlines()) # save the number of lines before closing file, we need to return
      
      os.close(fd)
  else:
      #f = os.open(source,os.O_RDONLY)
      with open(source,'r') as f:
      #data = os.read(f)
          data = f.read()
          if os.path.exists(target):
              os.remove(target)
          fd = os.open( target, os.O_RDWR|os.O_CREAT )
          uRet = os.write(fd,bytes(data,encoding='utf8')) # this variable has the size in bytes for the uncompressed file, we need to return 
          nLines = len(data.splitlines()) # save the number of lines before closing file, we need to return
          os.close(fd)
          f.close()



  return {"compSize": cSiz, "unCompSize": uRet, "numLines": nLines}

# this function fullfills the requisite of not using extensions to figure out compression

def whichComp(filepath):
    with open(filepath, 'rb') as test_f:
        check = binascii.hexlify(test_f.read(2))
        #return 
        if  (check == b'425a'):
            res = ("bz2")  
        elif (check == b'1f8b'):
            res = ("gz") 
            # b'504b' is zip
        else:
            res = "other"
            
    return res

#  command line options

if __name__ == "__main__":
    target = sys.argv[2]
    source = sys.argv[1]
    retby = exWithForce(source,target)
    typ = whichComp(source)
    print("wrote "+ str(retby['unCompSize']) + " bytes from file, compression type: " +str(typ) + ", number of lines: "+ str(retby['numLines']))
    