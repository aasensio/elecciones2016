from bs4 import BeautifulSoup
import urllib2
import numpy as np

# wiki = "http://en.wikipedia.org/wiki/Opinion_polling_for_the_Spanish_general_election,_2015"
# header = {'User-Agent': 'Mozilla/5.0'} #Needed to prevent 403 error on Wikipedia
# req = urllib2.Request(wiki,headers=header)
# page = urllib2.urlopen(req)
# result = page.read()
# f = open("page.html", "w")
# f.write(result)
# f.close()

f = open("page.html", "r")
page = f.read()
f.close()

soup = BeautifulSoup(page)
table = soup.find_all("table")[0]

rows = table.findAll('tr')
dat = []
loop = 0
for tr in rows[2:]:
	cols = tr.findAll('td')
	if (len(cols) == 14):
		temp = []
		for i in range(14):
			temp.append(cols[i].string)

	if (len(cols) == 13):
		temp = []
		for i in range(13):
			if (i == 11):
				temp.append('')
			temp.append(cols[i].string)

	if (len(cols) == 12):
		temp = []
		for i in range(12):
			if (i == 10 | i == 11):
				temp.append('')
			temp.append(cols[i].string)

	dat.append(temp)
