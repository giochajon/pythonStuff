import urllib3
from bs4 import BeautifulSoup

url = 'http://www.thefamouspeople.com/singers.php'

http = urllib3.PoolManager()
response = http.request('GET', url)
soup = BeautifulSoup(response.data.decode('utf-8'))
