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
    def __init__(self, dep_var='A3',
                 factors=['C', 'I(C**2)', 'I(C*Mn)', 'I(C*Si)', 'I(C*Cr)', 'I(C*Ni)',
                          'Mn', 'I(Mn**2)', 'I(Mn*Si)', 'I(Mn*Cr)', 'I(Mn*Ni)',
                          'Si', 'I(Si*Si)', 'I(Si*Cr)', 'I(Si*Ni)',
                          'Cr', 'I(Cr**2)', 'I(Cr*Ni)',
                          'Ni', 'I(Ni**2)']):
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


def filter_factors_by_pvalue(results, maxpvalue=.05):
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
        # drop factors with p-value > maxpvalue
        poly_2nd_deg.dropfactors(dropfactors[0])

        reg = smf.ols(poly_2nd_deg.formula, data=dataset)
        results = reg.fit()
        if printsummary:
            print(results.summary())
        it += 1

        dropfactors = filter_factors_by_pvalue(results, maxpvalue)

    print('{} iteration(s)'.format(it))

    return reg, results


if __name__ == '__main__':
    from plot_carbon_isopleth import load_reshape_dataset, select_carbon_isopleth, plot_carbon_isopleth

    fname_dataset = '../databases/Tcritical.csv'

    # dataset as pandas DataFrame
    dataset = load_dataset(fname_dataset)

    reg, results = {}, {}

    reg['A3hipo'], results['A3hipo'] = regression_poly_2nd_deg(
        dataset=dataset[dataset.eutectoid == 'hipo'],
        dep_var='A3', maxpvalue=.01,
        printsummary=False)

    reg['A3hiper'], results['A3hiper'] = regression_poly_2nd_deg(
        dataset=dataset[dataset.eutectoid == 'hiper'],
        dep_var='A3', maxpvalue=.01,
        printsummary=False)

    print(results['A3hipo'].summary())
    print(results['A3hiper'].summary())

    # plot isopleths
    fig, ax = plt.subplots()

    # multidimensional dataset as ordered dictionary
    dataset_multi = load_reshape_dataset(fname_dataset)
    Mn = 0
    Cr = 0
    Ni = 0

    for Si in range(dataset_multi['Si'].shape[2]):
        # experimental isopleth
        isopleth = select_carbon_isopleth(dataset_multi, Mn, Si, Cr, Ni)

        line, = plot_carbon_isopleth(
            isopleth, 'A3', ax,
            ls='none', marker='x',
            label='Si = {}'.format(Si))

        color = line.get_color()

        # predicted isopleth
        criteria = isopleth['eutectoid'] == 'hipo'
        prediction = results['A3hipo'].predict(isopleth)
        ax.plot(isopleth['C'][criteria], prediction[criteria], color=color)

        criteria = isopleth['eutectoid'] == 'hiper'
        prediction = results['A3hiper'].predict(isopleth)
        ax.plot(isopleth['C'][criteria], prediction[criteria], color=color)

    ax.legend()

    plt.show()
