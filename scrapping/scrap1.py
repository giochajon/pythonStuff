from bs4 import BeautifulSoup

import urllib3 
url = urllib3.urlopen("www.imdb.com")

content = url.read()

soup = BeautifulSoup(content)

links = soup.findAll("a")
