import sys
#get the name of the file 
myfile = sys.argv[1]
print("we are using ", myfile)


## get the number of lines
f = open(myfile,'r')

linenumber = len(f.readlines( ))

print("Number of Lines:",linenumber)


## get contents into z and number of chars
# move to the beginning
f.seek(0,0)

z = f.read()
numchars = len(z)
# how many "th" are in the file
thnum = z.count("th")
print (f"I found {thnum} th's in the file")

# tell will tell you the position on the file
if f.tell() == numchars:
    print(f'we are at char {numchars} at the end of file')

# move to the beginning
f.seek(0,0)



f.close()