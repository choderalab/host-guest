#! /usr/bin/env python2.7

from simtk.unit import *

import numpy as np

comments = "%#$@"

T=Quantity(298.15, kelvins) #Temperature not in slides, assume 25'C
R=Quantity(1.98720413, calories/(kelvin*mole)) 
c0=Quantity(1, moles/liters )

# Ka = exp(-dG/RT) / c0

ka_line=str()

with open("deltaGs.txt", "r") as dgfile:
    for line in dgfile:
	line = line.strip()
        if line[0] not in comments:
	    dG = Quantity( np.float64(line),kilocalories/mole)
	    Ka = np.exp(-1*dG/(R*T)) / c0
            ka_line += str(Ka)+ ", "

print ka_line
	    
           

