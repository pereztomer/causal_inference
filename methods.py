import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from xgboost.sklearn import XGBClassifier
import csv


def propensity_score_model(df, x, y):
    model = XGBClassifier().fit(df[x], df[y])

    return model


def s_learner(df, covariates):
    model = LinearRegression().fit(df[covariates + ['T']], df['Y'])

    all_zero_t = df[df['T'] == 1].copy()

    all_zero_t['T'] = 0

    return (model.predict(df[df['T'] == 1][covariates + ['T']]) -
            model.predict(all_zero_t[covariates + ['T']])).mean()


def t_learner(df, covariates):
    treated_model = LinearRegression().fit(df[df['T'] == 1][covariates], df[df['T'] == 1]['Y'])
    not_treated_model = LinearRegression().fit(df[df['T'] == 0][covariates], df[df['T'] == 0]['Y'])

    return (treated_model.predict(df[df['T'] == 1][covariates]) -
            not_treated_model.predict(df[df['T'] == 1][covariates])).mean()


def matching(df, covariates):
    model = KNeighborsRegressor(n_neighbors=1).fit(df[df['T'] == 0][covariates], df[df['T'] == 0]['Y'])

    matching_df = df[df['T'] == 1].copy()
    matching_df['Y_n'] = model.predict(matching_df[covariates])

    return (matching_df['Y'] - matching_df['Y_n']).mean()



def main():
    pass

if __name__ == '__main__':
    main()