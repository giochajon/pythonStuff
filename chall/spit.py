import binascii

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
    

x = whichComp ("./errors.log.bz2")
print (x)
x = whichComp ("./errors.log.gz")
print (x)
x = whichComp ("./errors.log")
print (x)
x = whichComp ("./errors.log.zip")
print (x)
x = whichComp ("./README.md")
print (x)