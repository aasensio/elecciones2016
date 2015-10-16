import numpy as np
import matplotlib.pyplot as pl
import pymc

data = np.loadtxt('votos.dat', skiprows=1)

nParties = 3
nElections = len(data[:,0])

lambdaFluxPSOE = pymc.Uniform('lambdaFluxPSOE', 0.0, 1e6, size=nParties-1)
lambdaFluxPP = pymc.Uniform('lambdaFluxPP', 0.0, 1e6, size=nParties-1)
lambdaFluxIU = pymc.Uniform('lambdaFluxIU', 0.0, 1e6, size=nParties-1)

avgPSOE = pymc.Uniform('avgPSOE', 0.0, 2e7)
avgPP = pymc.Uniform('avgPP', 0.0, 2e7)
avgIU = pymc.Uniform('avgIU', 0.0, 5e6)

fluxPSOE = pymc.Poisson("fluxPSOE", mu=lambdaFluxPSOE, size=nParties-1)
fluxPP = pymc.Poisson("fluxPP", mu=lambdaFluxPP, size=nParties-1)
fluxIU = pymc.Poisson("fluxIU", mu=lambdaFluxIU, size=nParties-1)

@pymc.deterministic(plot=False)
def lambdaPSOE(base=avgPSOE, flux=fluxPSOE):
	return base + np.sum(flux)	

@pymc.deterministic(plot=False)
def lambdaPP(base=avgPP, flux=fluxPP):
	return base + np.sum(flux)

@pymc.deterministic(plot=False)
def lambdaIU(base=avgIU, flux=fluxIU):
	return base + np.sum(flux)

votesPSOE = []
for i in range(nElections):
	votesPSOE.append(pymc.Poisson(name='votesPSOE'+str(i), mu=lambdaPSOE, value=data[i,0], observed=True))

votesPP = []
for i in range(nElections):
	votesPP.append(pymc.Poisson(name='votesPP'+str(i), mu=lambdaPP, value=data[i,1], observed=True))

votesIU = []
for i in range(nElections):
	votesIU.append(pymc.Poisson(name='votesIU'+str(i), mu=lambdaIU, value=data[i,2], observed=True))

# votesPSOE = pymc.Poisson('votesPSOE', mu=lambdaPSOE, size=nElections)#, value=data[:,1], observed=True)
# votesPP = pymc.Poisson('votesPP', mu=lambdaPP, value=data[:,2], observed=True)
# votesIU = pymc.Poisson('votesIU', mu=lambdaIU, value=data[:,3], observed=True)

# M = pymc.Model([lambdaFluxPSOE, lambdaFluxPP, lambdaFluxIU, fluxPSOE, fluxPP, fluxIU, 
	# lambdaPSOE, lambdaPP, lambdaIU, votesPSOE, votesPP, votesIU])

mcmc = pymc.MCMC([lambdaFluxPSOE, lambdaFluxPP, lambdaFluxIU, avgPSOE, avgPP, avgIU, 
	fluxPSOE, fluxPP, fluxIU, lambdaPSOE, lambdaPP, lambdaIU, votesPSOE, votesPP, votesIU])

mcmc.sample(15000, 1000)