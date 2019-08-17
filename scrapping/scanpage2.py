import urllib2, re
string = "movie"
source = urllib2.urlopen("http://imdb.com").read()
if re.search(word,source):
    print ("My search string: "+string)
