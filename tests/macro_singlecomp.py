"""
Given a simulation with index #, plot corresponding
RESULT_####.TXT and compare to Thermo-Calc macro simulation.

If option --replace is provided, replaces the critical temperatures
in the database.

If option --silent is provided, Thermo-Calc plot is not shown.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tctools import load_table, plot_table
import argparse
# Local modules
from parse_database import read_header_database, parse_header_database
from extract_Tcrit import extract_Tcrit

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('indices', nargs='+',
                        help='Test indices used to load Thermo-Calc table.')
    parser.add_argument('-r', '--replace', action='store_true',
                        help=('Replace database entry with results of the '
                              'new simulation'))
    parser.add_argument('-s', '--silent', action='store_true',
                        help=('Prevents plotting'))
    args = parser.parse_args()

    fdatabase = '../databases/Tcritical.csv'
    header = read_header_database(fdatabase)
    Trange, crange = parse_header_database(header)

    df = pd.read_csv(fdatabase, comment='#')

    for idx in args.indices:
        fname = '../results/{:05d}.DAT'.format(int(idx))

        if not args.silent:
            try:
                fig, ax = plt.subplots()
                result = load_table(fname, sort='T', fill=0)
                plot_table(df=result, xaxis='T', ax=ax, colpattern='NP(*)')
            except:
                print('Failed to plot {}'.format(fname))
            else:
                plt.pause(.1)
                fig.show()
                plt.pause(.1)

        idx, = np.where(fname == df['file'].values)
        if len(idx) > 0:
            idx = int(idx[0])
        else:
            continue

        row = df.iloc[[idx]]

        # Generates macro
        fmacro = open('macro_singlecomp.tcm', 'w')
        fmacro.write(('go data\n'
                      'def-el fe c mn si cr ni\n'
                      'rej ph *\n'
                      'rest ph fcc bcc cem\n'
                      'get\n'
                      'go p-3\n\n'
                      'ent-sy tab blab\n'
                      't x(*,*) np(*);\n\n'
                      's-a-v 1 t {:g} {:g} {:g}\n\n').format(Trange.min,
                                                             Trange.max,
                                                             Trange.step))

        wC = float(row['C'].values)
        wMn = float(row['Mn'].values)
        wSi = float(row['Si'].values)
        wCr = float(row['Cr'].values)
        wNi = float(row['Ni'].values)

        fmacro.write(('s-c n=1 p=101325 t=1173\n'
                      's-c w(c)={:g} w(mn)={:g} w(si)={:g}\n'
                      's-c w(cr)={:g} w(ni)={:g}\n'
                      'c-e\n'
                      'c-e\n').format(wC, wMn, wSi, wCr, wNi))

        fmacro.write('step,,\n')

        # output file
        # replace fname with results of new simulation
        # step: calculates equilibrium for each temperature
        # tab blab: saves table 'blab' to fout
        if args.replace:
            os.system('rm {}'.format(fname))
            fmacro.write(('tab,\n'
                          'blab,\n'
                          '{}\n').format(fname))

        if not args.silent:
            fmacro.write(('post\n'
                          's-l f\n'
                          'plot,,\n'))

            fmacro.write('set-int')
        fmacro.close()

        # run Thermo-Calc
        os.system('thermocalc macro_singlecomp.tcm')
        os.system('rm macro_singlecomp.tcm')

        if args.replace:
            A1, A1prime, A3, eutectoid = extract_Tcrit(fname)
            df.loc[idx, 'A1'] = A1
            df.loc[idx, 'A1prime'] = A1prime
            df.loc[idx, 'A3'] = A3
            df.loc[idx, 'eutectoid'] = eutectoid

            print('{} was replaced by new simulation results'.format(fname))

    if args.replace:
        file = open(fdatabase, 'w')
        file.write(header)
        file.close()
        df.to_csv(fdatabase, index=False, mode='a')
