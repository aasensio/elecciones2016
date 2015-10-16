# -*- coding: utf-8 -*-
import numpy as np
import xlrd
import numbers
import matplotlib.pyplot as pl
import seaborn as sn
import datetime as dt
import pyiacsun.machinelearn as ml
import matplotlib.dates as mdates

book = xlrd.open_workbook("sondeos.xlsx")
sh = book.sheet_by_index(0)

PP = []
PSOE = []
IU = []
UPyD = []
Podemos = []
Ciudadanos = []
fecha = []

mesEsp = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
mesEng = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

for rx in range(2,sh.nrows):
	row = sh.row_values(rx)	

	res = row[2]

	out = bytes(res, 'utf-8')
	res = out.replace(b'\xe2\x80\x93', b'-').decode('utf-8').lower()

	for i in range(12):
		res = res.replace(mesEsp[i], mesEng[i])

	res = res.replace('.', '')

	guion = res.find('-')

	if (guion != -1):
		res = res[guion+1:]

	out = res.split(' ')

	if ((len(out) > 1) and (res.find(')') == -1) ):
		if (len(out) == 2):
			res = '1 '+res

		PP.append(row[3])
		PSOE.append(row[4])
		IU.append(row[5])
		UPyD.append(row[6])
		Podemos.append(row[16])
		Ciudadanos.append(row[17])
		
		fecha.append(dt.datetime.strptime(res, "%d %b %Y").date())

partidos = [PP, PSOE, IU, UPyD, Podemos, Ciudadanos]
nSondeos = len(PP)
# Now clean the lists to transform percentages to numbers
for partido in partidos:
	for i in range(nSondeos):
		if (not isinstance(partido[i], numbers.Number)):
			findPct = partido[i].find('%')
			if (findPct != -1):
				res = 0.01*float(partido[i][0:findPct].replace(',', '.'))
				partido[i] = res
			else:
				partido[i] = 0

PP = np.asarray(PP)[::-1]
PSOE = np.asarray(PSOE)[::-1]
IU = np.asarray(IU)[::-1]
UPyD = np.asarray(UPyD)[::-1]
Podemos = np.asarray(Podemos)[::-1]
Ciudadanos = np.asarray(Ciudadanos)[::-1]
fecha = np.asarray(fecha)[::-1]
delta = np.zeros(len(fecha))
for i in range(len(fecha)):
	delta[i] = (fecha[i]-fecha[0]).days

partidos = [PP, PSOE, IU, UPyD, Podemos, Ciudadanos]
colors = ["blue", "red", "green", "magenta", "violet", "orange"]

pl.close()
f, ax = pl.subplots(nrows=1, ncols=1, figsize=(15,8))
ax.xaxis_date() 

gp = ml.GaussianProcess(delta)

deltaNew = np.copy(delta)
fechaNew = np.copy(fecha)
for i in range(150):
	deltaNew = np.append(deltaNew, delta[-1] + i+1)
	fechaNew = np.append(fechaNew, fecha[-1]+dt.timedelta(days=i+1))

for i in range(6):
	ax.plot(fecha, partidos[i], '.', color=sn.xkcd_rgb[colors[i]], linewidth=2)
	gp.fit(partidos[i], 0.1)
	predict, covariance = gp.predictNew(deltaNew)
	stddev = np.sqrt(np.diag(covariance))

	ax.plot(fechaNew, predict, color=sn.xkcd_rgb[colors[i]], linewidth=2)
	ax.plot(fechaNew, predict+2.0*stddev, '--', color=sn.xkcd_rgb[colors[i]], linewidth=1)
	ax.plot(fechaNew, predict-2.0*stddev, '--', color=sn.xkcd_rgb[colors[i]], linewidth=1)

f.autofmt_xdate()
ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
ax.xaxis.set_major_locator(mdates.MonthLocator())