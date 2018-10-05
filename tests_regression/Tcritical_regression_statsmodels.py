# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

import pandas as pd
from pandas.plotting import scatter_matrix

import statsmodels.api as sm
import statsmodels.formula.api as smf

from statsmodels.sandbox.regression.predstd import wls_prediction_std


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


class Formula:
    def __init__(self, dep_var, factors):
        self.dep_var = dep_var
        self.factors = factors.copy()

    def dropfactors(self, drop=[]):
        if isinstance(drop, str):
            drop = [drop]

        for factor in drop:
            factor = factor.replace(' ', '')
            self.factors.remove(factor)

    @property
    def formula(self):
        formula = '{} ~ '.format(self.dep_var)
        formula += ' + '.join(self.factors)

        return formula


def filter_factors_by_pvalue(results, maxpvalue=.01):
    pvalues = results.pvalues.sort_values(ascending=False)
    return list(pvalues.index[pvalues > maxpvalue])


def regression_poly_2nd_deg(dataset, dep_var, maxpvalue,
                            maxit=10, printsummary=False):
    """
    Arguments
    ---------
    dataset : pandas DataFrame
        dataset
    dep_var : string
        dependent variable
    maxpvalue : float
        maximum accepted p-value of each factor
        terms with p-value > maxpvalue are dropped
    maxit : integer, optional
        maximum number of iterations
        default : 10
    printsummary : boolean
        if True, print summary after each iteration
        default : False

    Return
    ------
    reg : statsmodels.regression.linear_model.OLS object
        regression
    results : statsmodels.regression.linear_model.RegressionResultsWrapper object
        regression results
    """
    # initialize formula
    poly_2nd_deg = Formula(dep_var=dep_var,
                           factors=['C', 'I(C**2)', 'I(C*Mn)', 'I(C*Si)', 'I(C*Cr)', 'I(C*Ni)',
                                    'Mn', 'I(Mn**2)', 'I(Mn*Si)', 'I(Mn*Cr)', 'I(Mn*Ni)',
                                    'Si', 'I(Si*Si)', 'I(Si*Cr)', 'I(Si*Ni)',
                                    'Cr', 'I(Cr**2)', 'I(Cr*Ni)',
                                    'Ni', 'I(Ni**2)'])

    # initialize regression; ols stands for 'ordinary least squares'
    reg = smf.ols(poly_2nd_deg.formula, data=dataset)
    # fit
    results = reg.fit()
    if printsummary:
        print(results.summary())
    it = 0

    # get factors with pvalue > maxpvalue
    dropfactors = filter_factors_by_pvalue(results, maxpvalue)

    while len(dropfactors) > 0 and it < maxit:
        # drop largest factor with p-value > maxpvalue
        poly_2nd_deg.dropfactors(dropfactors[0])

        reg = smf.ols(poly_2nd_deg.formula, data=dataset)
        results = reg.fit()
        if printsummary:
            print(results.summary())
        it += 1

        dropfactors = filter_factors_by_pvalue(results, maxpvalue)

    print('{} iteration(s)'.format(it))

    return reg, results


def plot_fitting_results(results, dataset, dep_var, ax=None, *args, **kwargs):
    if ax is None:
        fig, ax = plt.subplots()

    ax.plot(dataset[dep_var], results.predict(dataset), 'kx')

    lw, up = dataset[dep_var].min(), dataset[dep_var].max()
    ax.plot([lw, up], [lw, up], 'r-')

    ax.set_xlabel('True values')
    ax.set_ylabel('Predicted values')

    return ax


if __name__ == '__main__':
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
    dataset = load_dataset(fname_dataset)

    # dependent variable
    dep_var = 'A3'

    reg, results = {}, {}

    # Hipoeutectoid
    filtered_dataset = dataset[dataset.eutectoid == 'hipo']
    reg['hipo'], results['hipo'] = regression_poly_2nd_deg(
        dataset=filtered_dataset,
        dep_var=dep_var, maxpvalue=.01,
        printsummary=False)

    ax = plot_fitting_results(results['hipo'], filtered_dataset, dep_var)
    ax.set_title('{} hipo'.format(dep_var))

    print(results['hipo'].summary())

    # Hipereutectoid
    filtered_dataset = dataset[dataset.eutectoid == 'hiper']
    reg['hiper'], results['hiper'] = regression_poly_2nd_deg(
        dataset=filtered_dataset,
        dep_var=dep_var, maxpvalue=.01,
        printsummary=False)

    ax = plot_fitting_results(results['hiper'], filtered_dataset, dep_var)
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
