import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from xgboost import XGBClassifier
import csv


def propensity_score_model(df, x, y):
    model = XGBClassifier().fit(df[x], df[y])

    return model


def ipw(df, propensity_model, covariates):
    ipw_df = df.copy()
    ipw_df['propensity_score'] = propensity_model.predict_proba(ipw_df[covariates]).T[1]

    ipw_df['weighted_outcome'] = ipw_df.apply(lambda x: (x['propensity_score'] * x['Y']) /
                                                        (1 - x['propensity_score']), axis=1)

    ipw_df['propensity_score_norm_term'] = ipw_df.apply(lambda x: x['propensity_score'] /
                                                                  (1 - x['propensity_score']), axis=1)

    mean_of_treated = ipw_df[ipw_df['T'] == 1]['Y'].mean()
    mean_of_not_treated = ipw_df[ipw_df['T'] == 0]['weighted_outcome'].sum() / \
                                    ipw_df[ipw_df['T'] == 0]['propensity_score_norm_term'].sum()

    return mean_of_treated - mean_of_not_treated


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

    df = pd.read_csv('timeout/data/final_18.csv')

    df = df.drop(columns=['GAME_ID', 'TS', 'Unnamed: 0'])
    df = pd.get_dummies(df)
    covariates = list(df.columns)

    covariates.remove('Y')
    covariates.remove('T')

    propensity_model = propensity_score_model(df, covariates, 'T')

    ipw_att = ipw(df, propensity_model, covariates)
    # s_learner_att = s_learner(df, covariates)
    # t_learner_att = t_learner(df, covariates)
    # matching_att = matching(df, covariates)

    print('ATT Using IPW: ', ipw_att)
    # print('ATT Using S-Learner: ', s_learner_att)
    # print('ATT Using T-Learner: ', t_learner_att)
    # print('ATT Using Matching: ', matching_att)

if __name__ == '__main__':
    main()