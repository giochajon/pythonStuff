import sys
import hashlib as hash

# gio trying to replicate the results of the command: 
# echo "Hello World" | sha256sum 



def giocode(source):
	sha = hash.sha256()

	# Insert the string we want to hash

	sha.update(source.encode('utf-8'))
	# Print the hexadecimal format of the binary hash we just created
	#print sha.hexdigest()
	return sha.hexdigest()

if __name__ == "__main__":
    source = sys.argv[1]
    retby = giocode(source)
    print("received: "+source)
    print("result: "+retby)
