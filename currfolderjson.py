import os
import json
import pprint
#sources
# https://www.python.org/dev/peps/pep-0471/#os-scandir
# https://pypi.org/project/scandir/
# https://realpython.com/working-with-files-in-python/
#https://docs.python.org/3/library/pprint.html



path = os.getcwd()
#path = os.path.dirname(os.path.abspath(__file__))

## di contains all the files
di = os.listdir(path)
#print(di)


# ## function to get size of a directory and subs no symlinks
# def get_tree_size(path):
#     """Return total size of files in given path and subdirs."""
#     total = 0
#     for entry in os.scandir(path):
#         if entry.is_dir(follow_symlinks=False):
#             total += get_tree_size(entry.path)
#         else:
#             total += entry.stat(follow_symlinks=False).st_size
#     return total


 ## function to get size of a directory and subs no symlinks
def get_tree_size(pathsize):
    total = 0
    accum = 0 
    for entry in os.scandir(pathsize[0]):
        if entry.is_dir(follow_symlinks=False):
            accum += 1 # to count folders
            total += get_tree_size([entry.path,accum])[0]
            
        else:
            total += entry.stat(follow_symlinks=False).st_size
            accum += 1
    return [total,accum]





## check each if it is a directory no hidden files 
direc = {}
for file in di:
	if os.path.isdir(file) and not "." in file:
		##direc.update({file:os.path.getsize(file)})
		current = get_tree_size([file,0])
		direc.update({file:{"files":current[1],"size":current[0]} })

#sort the directories and listem in a column
#direc.sort()
##print (*direc, sep = "\n")

# inserting json into array 
a = []
a.append (direc)
b = {}
c = str(path)
b.update ({c:a})


##parsed =  json.dumps(direc, ensure_ascii=False)
parsed =  json.dumps(b, ensure_ascii=False)

## pprint(json.dumps(parsed, indent=4, sort_keys=True))
## get sizes add them in a dictionary
pp = pprint.PrettyPrinter(width=70, compact=False)
pp.pprint(parsed)


# find .txt files
# files = []
# # r=root, d=directories, f = files
# for r, d, f in os.walk(path):
#     for file in f:
#         if '.txt' in file:
#             files.append(os.path.join(r, file))

# print (files)