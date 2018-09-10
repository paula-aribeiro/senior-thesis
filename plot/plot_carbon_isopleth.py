"""
Reshape flattened dataframe into multidimensional numpy
arrays
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from collections import OrderedDict
# local module
from parse_database import read_header_database, parse_header_database


def get_idx_from_fname(fname):
    fname = fname.split('/')[-1]
    return int(fname.split('.')[0])


def load_dataset(fname):
    # read dataset
    dataset = pd.read_csv(fname, comment='#')

    # compositions to wt.%
    dataset.C *= 100
    dataset.Mn *= 100
    dataset.Si *= 100
    dataset.Cr *= 100
    dataset.Ni *= 100

    # temperatures to oC
    dataset.A1 -= 273.15
    dataset.A1prime -= 273.15
    dataset.A3 -= 273.15

    return dataset


def load_reshape_dataset(fname):
    # read database header to get data structure
    header = read_header_database(fname)
    # temperature range; composition range
    Trange, crange = parse_header_database(header)

    # read database
    df = load_dataset(fname)

    # get shape of multidimensional array
    newshape = []
    for el, rng in crange.items():
        newshape.append(rng.lvls)

    # reshape flattened dataframe as dictionary of multidimensional arrays
    dataset = OrderedDict()
    for key in df.columns:
        dataset[key] = df[key].values.reshape(newshape)

    return dataset


def select_carbon_isopleth(dataset, Mn=0, Si=0, Cr=0, Ni=0):
    isopleth = OrderedDict()

    for key, value in dataset.items():
        isopleth[key] = value[:, Mn, Si, Cr, Ni]

    isopleth['idx'] = np.array([get_idx_from_fname(fname)
                                for fname in isopleth['file']])

    return isopleth


def plot_carbon_isopleth(isopleth, dep_var='A3',
                         ax=None, *args, **kwargs):
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()

    idx = isopleth['idx']
    x = isopleth['C']
    y = isopleth[dep_var]

    annotate = kwargs.pop('annotate', False)
    lines = ax.plot(x, y, *args, **kwargs)

    if annotate:
        for idx_, x_, y_ in zip(idx, x, y):
            if ~np.isnan(x_) and ~np.isnan(y_):
                ax.text(x_, y_, str(idx_), size=10)

    return lines


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

    dataset = load_reshape_dataset('../databases/Tcritical.csv')

    # plot
    fig, ax = plt.subplots()

    i = 0
    while True:
        try:
            if args.free:
                args.free = args.free.lower()
                # vars: object -> dictionary
                vars(args)[args.free] = i

            isopleth = select_carbon_isopleth(
                dataset, args.mn, args.si, args.cr, args.ni)

            line, = plot_carbon_isopleth(
                isopleth, args.variable, ax, annotate=args.annotate)

            if args.free:
                line.set_label('{} = {}'.format(args.free.title(), i))
            else:
                break

            i += 1
        except Exception as ex:
            break

    if args.free:
        ax.legend()

    ax.set_xlabel('Carbon content (wt. %)')
    ax.set_ylabel('Temperature (°C)')
    plt.show()
