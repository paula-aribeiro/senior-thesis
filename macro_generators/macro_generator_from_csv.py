"""
Generates and Thermo-Calc macros
"""

import os
import numpy as np
import pandas as pd


def generate_macros_from_file(filename, chunksize=50):
    """
    Generate Thermo-Calc macros for step calculations for a given set of
    compositions provided in a csv file.

    Arguments
    ---------
    filename : string
        Path to the csv file
    chunksize : integer, optional
        Number of compositions calculated per macro
        Default value: 50

    Return
    ------
    macrolist : list
        List containing the file paths of all generated macros
    """

    # database with the [random] compositions
    df_comp = pd.read_csv(filename, comment='#')

    # basename (filename without extension)
    basename = os.path.basename(filename)
    basename = os.path.splitext(basename)[0]

    # Temperature
    T_min, T_max, T_step = 673., 1473., 10.

    # Code shared to all macros
    # blab: table containing phases compositions (x(*,*)) and phase fraction (np(*))
    common_snippet = ('go data\n'
                      'def-el fe c mn si cr ni\n'
                      'rej ph *\n'
                      'rest ph fcc bcc cem\n'
                      'get\n'
                      'go p-3\n\n'
                      'ent-sy tab blab\n'
                      't w(*,*) np(*);\n\n'
                      's-a-v 1 t {:g} {:g} {:g}\n\n').format(T_min, T_max, T_step)

    macrolist = []

    # splits macros into smaller macros
    chunkit = 0
    macronumber = 1
    newmacro = True

    for idx, comp in df_comp.iterrows():
        # wt.% to wt. fraction
        wC = comp['C']*1e-2
        wMn = comp['Mn']*1e-2
        wSi = comp['Si']*1e-2
        wCr = comp['Cr']*1e-2
        wNi = comp['Ni']*1e-2

        if newmacro:
            # Creates macro
            macroname = '../macros_thermocalc/macro_{}_{}.tcm'.format(
                basename, macronumber)
            macrolist.append(macroname)
            fmacro = open(macroname, 'w')
            fmacro.write(common_snippet)
            newmacro = False

        # set compositions
        fmacro.write(('s-c n=1 p=101325 t=1173\n'
                      's-c w(c)={:g} w(mn)={:g} w(si)={:g}\n'
                      's-c w(cr)={:g} w(ni)={:g}\n'
                      'c-e\n'
                      'c-e\n').format(wC, wMn, wSi, wCr, wNi))

        # output file
        fout = '../results/{}_{:05d}.DAT'.format(basename, idx)
        # step: calculates equilibrium for each temperature
        # tab blab: saves table 'blab' to fout
        fmacro.write(('step,,\n'
                      'tab,\n'
                      'blab,\n'
                      '{}\n').format(fout))

        fmacro.write('save RESULT.POLY3 y\n\n')

        chunkit += 1

        if chunkit >= chunksize:
            macronumber += 1
            chunkit = 0
            newmacro = True
            fmacro.close()

    fmacro.close()

    return macrolist


def run_macros(macrolist):
    for fname in macrolist:
        os.system('thermocalc {}'.format(fname))
        # break


if __name__ == '__main__':
    macrolist = generate_macros_from_file(
        '../databases/random_compositions_database.csv', 25)

    run_macros(macrolist)
