"""
Compare Thermo-Calc Tcritical to empirical equations
"""

import glob
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tctools import load_table, plot_table


def A1_Andrews(Ni=0, Mn=0, Si=0, Cr=0):
    return 723 - 16.9*Ni + 29.1*Si - 10.7*Mn + 16.9*Cr


def A3_Andrews(C=0, Ni=0, Mn=0, Si=0, Cr=0):
    return 910 - 203*C**.5 + 44.7*Si - 15.2*Ni - 30.0*Mn + 11.0*Cr


database = pd.read_csv('../databases/Tcritical.csv')


A1_empirical = A1_Andrews(
    100*database['Ni'], 100*database['Mn'], 100*database['Si'], 100*database['Cr'])
A3_empirical = A3_Andrews(100*database['C'], 100*database['Ni'],
                          100*database['Mn'], 100*database['Si'], 100*database['Cr'])

fig, ax = plt.subplots()

sel = (database['eutectoid'] == 'hipo') & (database['C'] > 0)

K = 273.15
ax.plot(database['A1'][sel] - K, A1_empirical[sel], 'kx', label='A1')
ax.plot(database['A3'][sel] - K, A3_empirical[sel], 'rx', label='A3')

x = list(ax.get_xlim())
ax.plot(x, x, 'b-')

ax.set_xlabel(u'T database Thermo-Calc (°C)')
ax.set_ylabel(u'T empirical (°C)')
ax.legend()

fig.savefig('comparison_Andrews_TC.png', dpi=300)

# add anotations and zoom in
sel = sel & (A1_empirical < database['A1'] - K)
for i in database[sel].index:
    ax.annotate(str(i), (database['A1'][sel][i] - K, A1_empirical[sel][i]), size=10)

ax.set_xlim(880, 2100)
ax.set_ylim(700, 850)

fig.savefig('comparison_Andrews_TC_detail.pdf')

plt.show()
