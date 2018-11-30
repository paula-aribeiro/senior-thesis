# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from tctools import load_table


def macro_generator(wC, wMn, wSi, wCr, wNi, T_min, T_max, T_step,
                    fresults='results.dat', macroname='macro.tcm'):
    fmacro = open(macroname, 'w')

    fmacro.write(('go data\n'
                  'def-el fe c mn si cr ni\n'
                  'rej ph *\n'
                  'rest ph fcc bcc cem\n'
                  'get\n'
                  'go p-3\n\n'
                  'ent-sy tab blab\n'
                  't np(*);\n\n'
                  's-a-v 1 t {:g} {:g} {:g}\n\n').format(T_min, T_max, T_step))

    # set compositions
    fmacro.write(('s-c n=1 p=101325 t=1173\n'
                  's-c w(c)={:g} w(mn)={:g} w(si)={:g}\n'
                  's-c w(cr)={:g} w(ni)={:g}\n'
                  'c-e\n'
                  'c-e\n').format(wC, wMn, wSi, wCr, wNi))

    # tab blab: saves table 'blab' to fout
    fmacro.write(('step,,\n'
                  'tab,\n'
                  'blab,\n'
                  '{}\n').format(fresults))

    fmacro.close()


def plot_diagram(fname, fout, title=None, **kwargs):
    df = load_table(fname, sort='T', fill=0)
    df['T'] -= 273.15

    # A1 = df['NP(BCC_A2)']
    # A1 = df['NP(FCC_A1#1)']

    fig, ax = plt.subplots(figsize=(4, 4))

    ax.plot(df['T'], df['NP(BCC_A2)'], label=r'$\alpha$ (ferrita)')
    ax.plot(df['T'], df['NP(FCC_A1#1)'], label=r'$\gamma$ (austenita)')
    try:
        ax.plot(df['T'], df['NP(CEMENTITE)'], label=r'$Fe_3C$ (cementita)')
    except:
        pass

    A1 = df['T'][df['NP(FCC_A1#1)'] == 0].max()
    ax.axvline(A1, ls=':', color='k')
    ax.annotate('A1', (A1, 1), va='bottom', ha='right')

    A3 = df['T'][df['NP(FCC_A1#1)'] == 1].min()
    ax.axvline(A3, ls=':', color='k')
    ax.annotate('A3', (A3, 1), va='bottom', ha='left')

    try:
        Tcem = df['T'][df['NP(CEMENTITE)'] == 0].min()
        Tbcc = df['T'][df['NP(BCC_A2)'] == 0].min()
    except:
        pass
    else:
        A1prime = Tcem if Tcem < Tbcc else Tbcc
        ax.axvline(A1prime, ls=':', color='k')
        ax.annotate('A1\'', (A1prime, 1), va='bottom', ha='left')

    ax.set_xlim(400, 1200)
    ax.set_ylim(-.05, 1.07)
    ax.set_xlabel(u'Temperatura (°C)')
    ax.set_ylabel(u'Fração molar da fase')
    if title is not None:
        ax.set_title(title)

    ax.legend()

    fig.savefig(fout, **kwargs)

    return fig, ax


if __name__ == '__main__':
    import os 

    T_min = 673.15
    T_max = 1473.15
    T_step = 10

    # hipo alloy
    macro_generator(1.5e-3, 1e-6, 2.25e-2, 1.5e-2, 3e-2, T_min, T_max, T_step, 'alloy_hipo.dat', 'macro.tcm')
    os.system('thermocalc macro.tcm')
    plot_diagram('ALLOY_HIPO.DAT', 'alloy_hipo.png', dpi=150)

    macro_generator(9e-3, 3e-2, 1.5e-2, 3e-2, 7.5e-3, T_min, T_max, T_step, 'alloy_hiper.dat', 'macro.tcm')
    os.system('thermocalc macro.tcm')
    plot_diagram('ALLOY_HIPER.DAT', 'alloy_hiper.png', dpi=150)

    macro_generator(0, 7.5e-3, 2.25e-2, 2.25e-2, 2.25e-2, T_min, T_max, T_step, 'alloy_nocem.dat', 'macro.tcm')
    os.system('thermocalc macro.tcm')
    plot_diagram('ALLOY_NOCEM.DAT', 'alloy_nocem.png', dpi=150)
