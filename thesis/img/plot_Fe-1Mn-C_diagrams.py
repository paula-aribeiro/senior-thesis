# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from tctools import load_table

files = ['FE-1MN-0.4C.TXT', 'FE-1MN-0.727C.TXT', 'FE-1MN-1C.TXT']
titles = [u'0,1%C (hipoeutetóide)', u'0,727%C (eutetóide)',
          u'1%C (hipereutetóide)']

for idx, (fname, title) in enumerate(zip(files, titles)):
    df = load_table(fname, sort='T', fill=0)
    df['T'] -= 273.15

    # A1 = df['NP(BCC_A2)']
    # A1 = df['NP(FCC_A1)']

    fig, ax = plt.subplots(figsize=(4, 4))

    ax.plot(df['T'], df['NP(BCC_A2)'], label=r'$\alpha$ (ferrita)')
    ax.plot(df['T'], df['NP(FCC_A1)'], label=r'$\gamma$ (austenita)')
    ax.plot(df['T'], df['NP(CEMENTITE)'], label=r'$Fe_3C$ (cementita)')

    A1 = df['T'][df['NP(FCC_A1)'] == 0].max()
    ax.axvline(A1, ls=':', color='k')
    ax.annotate('A1', (A1, 1), va='bottom', ha='right')

    A3 = df['T'][df['NP(FCC_A1)'] == 1].min()
    ax.axvline(A3, ls=':', color='k')
    ax.annotate('A3', (A3, 1), va='bottom', ha='left')

    if idx == 0:
        A1prime = df['T'][df['NP(CEMENTITE)'] == 0].min()
        ax.axvline(A1prime, ls=':', color='k')
        ax.annotate('A1\'', (A1prime, 1), va='bottom', ha='left')
    elif idx == 2:
        A1prime = df['T'][df['NP(BCC_A2)'] == 0].min()
        ax.axvline(A1prime, ls=':', color='k')
        ax.annotate('A1\'', (A1prime, 1), va='bottom', ha='left')

    ax.set_xlim(650, 850)
    ax.set_ylim(-.05, 1.07)
    ax.set_xlabel(u'Temperatura (°C)')
    ax.set_ylabel(u'Fração molar da fase')
    ax.set_title(title)

    ax.legend()

    fout = os.path.splitext(fname)[0].replace('.', '') + '.png'
    fig.tight_layout()
    fig.savefig(fout, dpi=150)

    # break

# plt.show()
plt.close('all')
