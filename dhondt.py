#!/usr/bin/env python3
# −*− coding: UTF−8 −*−

import sys
from argparse import ArgumentParser


class dhondt():
    """Class to calculate d'Hondt statistics

    :Authors: Pedro Ferrer, Silvia Fuentes
    :Date: 2015-07-20
    :version: 1.1

    The minimum data to be providen is:

    + The number of seats [nseats]
    + The minimum percentage to get into the calculation [minper]
    + A dictionary with the votes of the candidatures [dcandi]
         dcandi = {'000001': 51000, '000002': 46000, '000007': 34000, '000006': 29000, 'others': 31000}

    CAVEAT LECTOR
    + It doesn't resolve seat ties
    + Always gets rid of a party called 'others'
    """
    def __init__(self, nseats, minper, dcandi, census=0, blankv=0, sploitv=0, bmp=False):
        self.nseats = nseats
        self.minper = minper
        self.census = census
        self.blankv = blankv
        self.sploitv = sploitv
        self.dcandi = dcandi.copy()
        self.bmp = bmp
        self.calc()

    def __repr__(self):
        candidatures = sorted(self.dcandi.items(), key=lambda p: p[1], reverse=True)
        return '<dhondt nseats:{0} minper:{1} candi:{2}>'.format(self.nseats, self.minper, candidatures)

    @property
    def nseats(self):
        return self.__nseats

    @nseats.setter
    def nseats(self, nseats):
        if type(nseats) is int and nseats > 0:
            self.__nseats = nseats
        else:
            raise AttributeError('The number or seats value must be an integer greater than 0')

    @property
    def minper(self):
        return self.__minper

    @minper.setter
    def minper(self, minper):
        if type(minper) is float and minper > 0:
            self.__minper = minper
        else:
            raise AttributeError('The minimum percentage value must be a float greater than 0')

    @property
    def census(self):
        return self.__census

    @census.setter
    def census(self, census):
        if type(census) is int:
            self.__census = census
        else:
            raise AttributeError('The census value must be an integer')

    @property
    def blankv(self):
        return self.__blankv

    @blankv.setter
    def blankv(self, blankv):
        if type(blankv) is int:
            self.__blankv = blankv
        else:
            raise AttributeError('The blank votes value must be an integer')

    @property
    def sploitv(self):
        return self.__sploitv

    @sploitv.setter
    def sploitv(self, sploitv):
        if type(sploitv) is int:
            self.__sploitv = sploitv
        else:
            raise AttributeError('The sploit votes value must be an integer')

    @property
    def dcandi(self):
        return self.__dcandi

    @dcandi.setter
    def dcandi(self, dcandi):
        if type(dcandi) is dict:
            self.__dcandi = dcandi.copy()
            try:
                sum(dcandi.values())
            except TypeError:
                raise AttributeError('The candidatures votes values must be integers')
        else:
            raise AttributeError('The candidatures data must be a dictionary')

    @property
    def bmp(self):
        return self.__bmp

    @bmp.setter
    def bmp(self, bmp):
        if type(bmp) is bool:
            self.__bmp = bmp
        else:
            raise AttributeError('The blank votes count for minimum percentage flag must be a Boolean ')

    def __mindata(self):
        if self.nseats and self.minper and self.dcandi:
            return True
        return False

    def calc(self):
        """Performs the calculation"""
        if not self.__mindata():
            sys.exit('Minimum data not set')
        vtot = sum(self.dcandi.values())
        # TODO: Finish script with the RESULTS and PARTICIPATION sections
        #ncan = len(self.dcandi)
        #if self.census < (vtot + self.blankv + self.sploitv):
            #bvcensus = False
            #self.census = 0
            #nabs = 0
        #else:
            #bvcensus = True
            #nabs = self.census - vtot - self.blankv - self.sploitv
        # Sort the candidatures in descending number of votes
        candidatures = sorted(self.dcandi.items(), key=lambda p: p[1], reverse=True)
        if self.bmp:
            minvot = (((vtot + self.blankv) * self.minper) / 100) - 1
        else:
            minvot = ((vtot * self.minper) / 100) - 1
        # Filter the candidatures that have not reached the minimum
        candismin = list(filter(lambda p: p[1] > minvot, candidatures))
        candivali = list(filter(lambda p: p[0] != 'other', candismin))
        #candirest = list(filter(lambda p: p[1] < minvot + 1, candidatures))

        # Prepare the lists for the calculations
        candinames = [p[0] for p in candivali]
        candimaxis = [p[1] for p in candivali]
        canditrab = [(p[1], 0) for p in candivali]

        # Prepare the dictionaries for the results
        self.repre = dict(zip(candinames, [0 for name in candinames]))
        self.asigna = dict(zip(candinames, [[maxi] for maxi in candimaxis]))

        # Perform the seat calculation
        for i in range(self.nseats):
            # Find the party with the maximum nunber of votes in this round
            dic01 = dict(zip(candinames, canditrab))
            odic01 = sorted(dic01.items(), key=lambda p: p[1][0], reverse=True)
            parmax = odic01[0][0]
            inparmax = candinames.index(parmax)
            maxivotos = candimaxis[inparmax]
            nseatsre = canditrab[inparmax][1]
            # This line does the magic
            canditrab[inparmax] = (maxivotos / (nseatsre + 2), nseatsre + 1)
            self.repre[parmax] = nseatsre + 1
            # Fill the asignation table dictionary
            for j, trab in enumerate(canditrab):
                self.asigna[candinames[j]].append(int(trab[0]))
            # We need to know which was the party assigned with the seat before the last seat
            if i == self.nseats - 2:
                penparmax = parmax
            else:
                penparmax = parmax

        # Calculate the votes needed for another seat
        self.falta = {}
        votult = self.asigna[parmax][-2]

        for name in candinames:
            votu = self.dcandi[name]
            crep = self.repre[name]
            if name == parmax:
                # The last asigned seat gets the number differently
                crepp = self.repre[penparmax]
                votp = self.dcandi[penparmax]
                vfalta = int(votp / crepp * (crep + 1) - votu)
            else:
                cvot = self.asigna[name][-1]
                vfalta = int((votult - cvot) * (crep + 1))
            pfalta = (vfalta / votu) * 100.0
            # Stores the number of votes and the percentage over the actual votes
            self.falta[name] = (vfalta, pfalta)


if __name__ == '__main__':
    """Performs the d'Hondt seats calculation

    $ python dhondt.py  21 3.0 "{'a': 100, 'b': 200}"
    """
    baseparser = ArgumentParser(description="Performs the d'Hondt seats calculation")
    group_min = baseparser.add_argument_group('Minimum data')
    group_min.add_argument('nseats', help='Number of seats for the calculation')
    group_min.add_argument('minper', help='Minimun percentage of votes to enter in the calculation')
    group_min.add_argument('datcan', help='Dictionary with the candidatures data')
    args = vars(baseparser.parse_args())
    # Gets the input data
    ## nseats, minper, census, white, sploitv, nabs, dcandi
    nseats = int(args['nseats'])
    minper = float(args['minper'])
    dcandi = dict((k, eval(v)) for (k, v) in [it.split(':') for it in args['datcan'].replace("'", "").strip('{}').split(', ')])
    # Performs the dhont calc
    result = dhondt(nseats, minper, dcandi)
    # Returns data calc
    print(result)
    print('<seats: {0}>'.format(sorted(result.repre.items(), key=lambda p: p[1], reverse=True)))
