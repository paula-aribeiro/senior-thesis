"""
Generates and Thermo-Calc macros
"""

import os
import numpy as np
import pandas as pd

# Empty macros directory
os.system('rm ../macros_thermocalc/macro*tcm')

# Compositions
C_min, Mn_min, Si_min, Cr_min, Ni_min = 0, 1e-6, 1e-6, 1e-6, 1e-6
C_max, Mn_max, Si_max, Cr_max, Ni_max = 1.5e-2, 3e-2, 3e-2, 3e-2, 3e-2
C_lvls, Mn_lvls, Si_lvls, Cr_lvls, Ni_lvls = 11, 5, 5, 5, 5

C, Mn, Si, Cr, Ni = np.mgrid[C_min:C_max:C_lvls*1j,
                             Mn_min:Mn_max:Mn_lvls*1j,
                             Si_min:Si_max:Si_lvls*1j,
                             Cr_min:Cr_max:Cr_lvls*1j,
                             Ni_min:Ni_max:Ni_lvls*1j]

C = C.ravel()
Mn = Mn.ravel()
Si = Si.ravel()
Cr = Cr.ravel()
Ni = Ni.ravel()

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

filelist = []
currmacro = []
macrolist = []

# splits macros into smaller macros
chunkit = 0
chunksize = 50
macronumber = 1
newmacro = True

for idx, (wC, wMn, wSi, wCr, wNi) in enumerate(zip(C, Mn, Si, Cr, Ni)):
    if newmacro:
        # Creates macro
        macroname = '../macros_thermocalc/macro_{}.tcm'.format(macronumber)
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
    fout = '../results/{:05d}.DAT'.format(idx)
    # step: calculates equilibrium for each temperature
    # tab blab: saves table 'blab' to fout
    fmacro.write(('step,,\n'
                  'tab,\n'
                  'blab,\n'
                  '{}\n').format(fout))

    fmacro.write('save RESULT.POLY3 y\n\n')

    chunkit += 1

    filelist.append(fout)
    currmacro.append(macroname)

    if chunkit >= chunksize:
        macronumber += 1
        chunkit = 0
        newmacro = True
        fmacro.close()

fmacro.close()

df = pd.DataFrame(dict(file=filelist, macro=currmacro, C=C, Mn=Mn, Si=Si, Cr=Cr, Ni=Ni),
                  columns=['file', 'macro', 'C', 'Mn', 'Si', 'Cr', 'Ni'])

# saving df to fname
fname = '../databases/compositions_files.csv'
file = open(fname, 'w')
file.write(('# T {:g}:{:g}:{:g}\n'
            '# C {:g}:{:g}:{:d}j\n'
            '# Mn {:g}:{:g}:{:d}j\n'
            '# Si {:g}:{:g}:{:d}j\n'
            '# Cr {:g}:{:g}:{:d}j\n'
            '# Ni {:g}:{:g}:{:d}j\n').format(T_min, T_max, T_step,
                                             C_min, C_max, C_lvls,
                                             Mn_min, Mn_max, Mn_lvls,
                                             Si_min, Si_max, Si_lvls,
                                             Cr_min, Cr_max, Cr_lvls,
                                             Ni_min, Ni_max, Ni_lvls))
file.close()
df.to_csv(fname, index=False, mode='a')

# Clear results
os.system('rm ../results/*DAT')

for fname in macrolist:
    os.system('thermocalc {}'.format(fname))
    # break
