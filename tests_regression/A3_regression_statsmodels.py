import Tcritical_regression_statsmodels as tr
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import root
from parse_database import read_header_database, parse_header_database
from plot_carbon_isopleth import (load_reshape_dataset,
                                  select_carbon_isopleth,
                                  plot_carbon_isopleth)

fname_dataset = '../databases/Tcritical.csv'

header = read_header_database(fname_dataset)
# Temperature range and compositions ranges
Trange, crange = parse_header_database(header)

# dataset as pandas DataFrame
dataset = tr.load_dataset(fname_dataset)

# dependent variable
dep_var = 'A3'

reg, results = {}, {}

# Hipoeutectoid
filtered_dataset = dataset[dataset.eutectoid == 'hipo']
reg['hipo'], results['hipo'] = tr.regression_poly_2nd_deg(
    dataset=filtered_dataset,
    dep_var=dep_var, maxpvalue=.01,
    printsummary=False)

ax = tr.plot_fitting_results(results['hipo'], filtered_dataset, dep_var)
ax.set_title('{} hipo'.format(dep_var))

print(results['hipo'].summary())

# Hipereutectoid
filtered_dataset = dataset[dataset.eutectoid == 'hiper']
reg['hiper'], results['hiper'] = tr.regression_poly_2nd_deg(
    dataset=filtered_dataset,
    dep_var=dep_var, maxpvalue=.01,
    printsummary=False)

ax = tr.plot_fitting_results(results['hiper'], filtered_dataset, dep_var)
ax.set_title('{} hiper'.format(dep_var))

print(results['hiper'].summary())

def A3(C=0, Mn=0, Si=0, Cr=0, Ni=0):
    """
    A3 temperature for either hipo or hipereutectoid alloy
    """
    def Thipo(C):
        df = pd.DataFrame(dict(C=C, Mn=Mn, Si=Si, Cr=Cr, Ni=Ni))
        return results['hipo'].predict(df)

    def Thiper(C):
        df = pd.DataFrame(dict(C=C, Mn=Mn, Si=Si, Cr=Cr, Ni=Ni))
        return results['hiper'].predict(df)

    Ceut = root(fun=lambda x: Thipo(x) - Thiper(x), x0=.75)
    print(Ceut)
    Ceut = Ceut.x[0]

    T = np.ndarray(C.shape)
    T[C <= Ceut] = Thipo(C[C <= Ceut])
    T[C > Ceut] = Thiper(C[C > Ceut])

    return T

# plot isopleths
fig, ax = plt.subplots()

# multidimensional dataset as ordered dictionary
dataset_multi = load_reshape_dataset(fname_dataset)

# compositions (level)
Mn = 0
Si = 0
Cr = 0
Ni = 0

# compositions (wt.%)
C_ = 100*np.linspace(crange['C'].min, crange['C'].max, 100)

for Mn in range(5):
    # compositions (wt.%)
    Mn_ = 100*crange['Mn'].array[Mn]
    Si_ = 100*crange['Si'].array[Si]
    Cr_ = 100*crange['Cr'].array[Cr]
    Ni_ = 100*crange['Ni'].array[Ni]

    # experimental isopleth
    isopleth = select_carbon_isopleth(dataset_multi, Mn, Si, Cr, Ni)

    line, = plot_carbon_isopleth(isopleth, dep_var, ax,
                                 ls='none', marker='x',
                                 annotate=True)

    # predicted isopleth
    if dep_var == 'A3':
        ax.plot(C_, A3(C_, Mn_, Si_, Cr_, Ni_), color=line.get_color())

    else:
        criteria = isopleth['eutectoid'] == 'hipo'
        ax.plot(isopleth['C'][criteria],
                results['hipo'].predict(isopleth)[criteria],
                color=line.get_color())

        criteria = isopleth['eutectoid'] == 'hiper'
        ax.plot(isopleth['C'][criteria],
                results['hiper'].predict(isopleth)[criteria],
                color=line.get_color())

plt.show()
