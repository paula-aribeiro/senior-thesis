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
newshape = []
for el, rng in crange.items():
    newshape.append(rng.lvls)

# reshaple flattened dataframe
dbmulti = OrderedDict()
for key in db.columns:
    dbmulti[key] = db[key].values.reshape(newshape)


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--annotate', action='store_true',
                        help='Annotate plot')
    parser.add_argument('-f', '--free', default=None,
                        help='Free variable besides carbon (e.g, try setting -free mn)')
    parser.add_argument('-v', '--variable', default='A3',
                        help='Which (dependent) variable to plot. Default: A3 temperature')

    parser.add_argument('--mn', type=int, default=0,
                        help='Amount of Mn expressed in terms of levels. Default: 0')
    parser.add_argument('--si', type=int, default=0,
                        help='Amount of Si expressed in terms of levels. Default: 0')
    parser.add_argument('--cr', type=int, default=0,
                        help='Amount of Cr expressed in terms of levels. Default: 0')
    parser.add_argument('--ni', type=int, default=0,
                        help='Amount of Ni expressed in terms of levels. Default: 0')

    args = parser.parse_args()

    def parse_fname(fname):
        fname = fname.split('/')[-1]
        return int(fname.split('.')[0])

    # plot
    fig, ax = plt.subplots()

    i = 0
    while True:
        try:
            if args.free:
                vars(args)[args.free] = i

            x = dbmulti['C'][:, args.mn, args.si, args.cr, args.ni]
            y = dbmulti[args.variable][:, args.mn, args.si, args.cr, args.ni]
            files = dbmulti['file'][:, args.mn, args.si, args.cr, args.ni]

            for j, fname in enumerate(files):
                idx = parse_fname(fname)
                if args.annotate:
                    if not np.isnan(x[j]) and not np.isnan(y[j]):
                        ax.text(x[j], y[j], str(idx), size=10)

            line, = ax.plot(x, y, marker='x')

            if args.free:
                line.set_label('{} {}'.format(args.free, i))
            else:
                break

            i += 1
        except Exception as ex:
            break

    if args.free:
        ax.legend()
    ax.set_xlabel('Carbon content (wt. fraction)')
    ax.set_ylabel('Temperature (K)')
    plt.show()
