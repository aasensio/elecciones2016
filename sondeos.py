# -*- coding: utf-8 -*-
import numpy as np
import xlrd
import numbers
import matplotlib.pyplot as pl
import seaborn as sn
import datetime as dt
import matplotlib.dates as mdates
import scipy.integrate as integ
import scipy.interpolate as interp
from ipdb import set_trace as stop
import nestle
import pyiacsun as ps
from numba import jit
import emcee
import transforms as tr

def euler( f, x0, t ):
    """Euler's method to solve x' = f(x,t) with x(t[0]) = x0.

    USAGE:
        x = euler(f, x0, t)

    INPUT:
        f     - function of x and t equal to dx/dt.  x may be multivalued,
                in which case it should a list or a NumPy array.  In this
                case f must return a NumPy array with the same dimension
                as x.
        x0    - the initial condition(s).  Specifies the value of x when
                t = t[0].  Can be either a scalar or a list or NumPy array
                if a system of equations is being solved.
        t     - list or NumPy array of t values to compute solution at.
                t[0] is the the initial condition point, and the difference
                h=t[i+1]-t[i] determines the step size h.

    OUTPUT:
        x     - NumPy array containing solution values corresponding to each
                entry in t array.  If a system is being solved, x will be
                an array of arrays.
    """

    n = len( t )
    x = np.array( [x0] * n )
    for i in range( n - 1 ):
        x[i+1] = x[i] + ( t[i+1] - t[i] ) * f( x[i], t[i] )

    return x


class sondeos(object):
    def __init__(self, nNodes):
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

        self.obsTime = delta
        self.party = np.asarray(partidos).T
        self.nParties = self.party.shape[1]
        self.nNodes = nNodes
        self.timeNodes = np.linspace(delta[0], delta[-1], self.nNodes)
        self.initialCondition = np.zeros(self.nParties)
        for i in range(self.nParties):
            self.initialCondition[i] = self.party[0,i]

        ind = np.all(self.party != 0, axis=1)
        self.party = self.party[ind,:]
        self.obsTime = self.obsTime[ind]
        self.nTimes = len(self.obsTime)

        ind = np.argsort(self.obsTime)
        self.obsTime = self.obsTime[ind]
        for i in range(6):
            self.party[:,i] = self.party[ind,i]

        self.obsTime -= self.obsTime[0]
        self.low = -1
        self.up = 1

    #@profile
    def funODE(self, y, t0):
        ind = np.where()
        return matrix.dot(y)

    #@profile
    def logLikelihood(self, thetaIn):

        theta, lnJactheta = tr.lrBoundedForward(thetaIn, self.low, self.up)
        
        matrix = theta.reshape((self.nNodes,self.nParties,self.nParties))

        self.matrix = np.zeros((self.nTimes,self.nParties,self.nParties))
        for i in range(self.nParties):
            for j in range(self.nParties):
                tmp = interp.UnivariateSpline(self.timeNodes, matrix[:,i,j])
                self.matrix[:,i,j] = tmp(self.obsTime)

        out = np.zeros((self.nTimes,self.nParties))
        out[0,:] = self.initialCondition
        for i in range(self.nTimes-1):
            out[i+1,:] = out[i,:] + ( self.obsTime[i+1] - self.obsTime[i] ) * self.matrix[i,:,:].dot(out[i,:])

        logL = np.sum( (out[1:,:] - self.party[1:,:])**2 / 0.1**2 )

        #print(logL)
        

        return logL + np.sum(lnJactheta)

    def prior_transform(self, x):
        return (self.up - self.low) * x + self.low

    def sample(self):
        res = nestle.sample(self.logLikelihood, self.prior_transform, self.nNodes*36, method='single', npoints=1000)

    def sample_emcee(self, nIterations):
        ndim = self.nNodes*36
        self.nwalkers = 2 * ndim
        self.theta0 = np.zeros(ndim)
        
        p0 = [self.theta0 + 1e-4*np.random.randn(ndim) for i in range(self.nwalkers)]
        self.sampler = emcee.EnsembleSampler(self.nwalkers, ndim, self.logLikelihood)

        loop = 0

        self.chain = np.zeros((nIterations,self.nwalkers,ndim))
    
        for result in self.sampler.sample(p0, iterations=nIterations, storechain=False):
            out, _ = tr.lrBoundedForward(result[0], self.low, self.up)
            self.chain[loop,:,:] = out
            ps.util.progressbar(loop, nIterations, text='sampling')
            loop += 1
           
out = sondeos(4)
out.sample_emcee(1000)
np.save('sampling.mcmc', out.chain)

