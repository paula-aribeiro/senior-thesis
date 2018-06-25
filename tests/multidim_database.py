"""
Reshape flattened dataframe into multidimensional numpy
arrays
"""

import numpy as np
import pandas as pd
from collections import OrderedDict
# local module
from parse_database import read_header_database, parse_header_database

fname = '../databases/Tcritical.csv'

# read database header to get data structure
header = read_header_database(fname)
# temperature range; composition range
trange, crange = parse_header_database(header)
db = pd.read_csv(fname, comment='#')

# get shape of multidimensional array
shape = []
for el, rng in crange.items():
    shape.append(rng.lvls)
print(shape)

# reshaple flattened dataframe
dbmulti = OrderedDict()
for key in db.columns:
    dbmulti[key] = db[key].values.reshape(shape)


# plot
import matplotlib.pyplot as plt


def parse_fname(fname):
    fname = fname.split('/')[-1]
    return int(fname.split('.')[0])


fig, ax = plt.subplots()
for i in range(5):
    x = dbmulti['C'][:, 1, i, 3, 3]
    y = dbmulti['A3'][:, 1, i, 3, 3]

    for j, fname in enumerate(dbmulti['file'][:, 1, i, 3, 3]):
        idx = parse_fname(fname)
        ax.annotate(str(idx), (x[j], y[j]), size=10)

    ax.plot(x, y, marker='x')

ax.set_xlabel('Carbon content (wt. fraction)')
ax.set_ylabel('Temperature (K)')
plt.show()
