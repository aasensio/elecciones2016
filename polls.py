from bs4 import BeautifulSoup
import urllib2
import numpy as np
import matplotlib.pyplot as pl

wiki = "http://en.wikipedia.org/wiki/Opinion_polling_for_the_Spanish_general_election,_2015"
header = {'User-Agent': 'Mozilla/5.0'} #Needed to prevent 403 error on Wikipedia
req = urllib2.Request(wiki,headers=header)
page = urllib2.urlopen(req)
soup = BeautifulSoup(page)

table = soup.find_all("table")[0]

final = []
for row in table.findAll("tr"):
	cells = row.findAll("td")
	print len(cells), cells
	if (len(cells) <= 12):
		res = [None] * 14
		for i in range(14):
			res[i] = cells[i].find(text=True)
		final.append(res)

nData = len(final)

partidos = {'PP': np.zeros(nData), 'PSOE': np.zeros(nData), 'IU': np.zeros(nData), 'UPyD': np.zeros(nData)}
res = np.zeros(nData)
for i in range(nData):
	partidos['PP'][i] = final[i][2]
	partidos['PSOE'][i] = final[i][3]

