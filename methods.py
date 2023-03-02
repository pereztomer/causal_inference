import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor, NearestNeighbors
from xgboost import XGBClassifier
import matplotlib.pyplot as plt


def propensity_score_model(df, x, y):
    model = XGBClassifier().fit(df[x], df[y])

    return model


def calculate_ate_ipw(df, propensity_model):
    df['weights'] = 1 / propensity_model.predict_proba(df[['T', 'Y']])[:, 1]
    treated_group = df[df['T'] == 1]
    control_group = df[df['T'] == 0]
    ate = np.average(treated_group['Y'],
                     weights=treated_group['weights']) - np.average(control_group['Y'],
                                                                    weights=control_group['weights'])
    return ate


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


def knn_matching_ate_ci(df, t_col, y_col, covariates, k=5, num_bootstrap=100, alpha=0.05):
    treated = df[df[t_col] == 1]
    untreated = df[df[t_col] == 0]
    covariates = covariates

    # Perform KNN matching on the covariates
    knn = NearestNeighbors(n_neighbors=1)
    knn.fit(untreated[covariates])
    dist, matches = knn.kneighbors(treated[covariates])
    matches = pd.DataFrame({'treatment': treated.index,
                            'match': untreated.index[matches[:, 0]]})

    # Calculate ATE by comparing treated and matched untreated groups
    matched = pd.concat([treated, untreated.loc[matches['match']]], axis=0)
    ate = matched[y_col].mean() - matched.loc[matches['match']][y_col].mean()

    # Bootstrap to estimate confidence interval
    ates = []
    for i in range(num_bootstrap):
        sample = df.sample(frac=1, replace=True)
        t_sample = sample[sample[t_col] == 1]
        u_sample = sample[sample[t_col] == 0]
        knn = NearestNeighbors(n_neighbors=k)
        knn.fit(u_sample[covariates])
        dist, matches = knn.kneighbors(t_sample[covariates])
        matches = pd.DataFrame({'treatment': t_sample.index,
                                'match': u_sample.index[matches[:, 0]]})
        matched = pd.concat([t_sample, u_sample.loc[matches['match']]], axis=0)
        ate_boot = matched[y_col].mean() - matched.loc[matches['match']][y_col].mean()
        ates.append(ate_boot)

    # Calculate confidence interval
    ci_lower = np.percentile(ates, alpha / 2 * 100)
    ci_upper = np.percentile(ates, (1 - alpha / 2) * 100)

    return ate, ci_lower, ci_upper


def main():

    df = pd.read_csv('timeout/data/final_timeout_ds.csv.csv')

    print(len(df))

    # df = pd.get_dummies(df)
    covariates = list(df.columns)# [col for col in list(df.columns) if 'avg' not in col]

    covariates.remove('Y')
    covariates.remove('T')
    covariates.remove('TEAM_ABBREVIATION_curr')
    covariates.remove('TEAM_ABBREVIATION_opponent')

    ci_left = []
    ci_right = []
    ci_center = []

    i = 0
    for team in df['TEAM_ABBREVIATION_curr'].unique():
        print(team + ':', end=' ')
        center, left, right = knn_matching_ate_ci(df[df['TEAM_ABBREVIATION_curr'] == team].dropna(), 'T', 'Y', covariates)
        print(f'ATE = {center}, CI = [{left}, {right}]')
        plt.plot([left, right], [i, i], linewidth=3, color='cyan')
        plt.scatter([center], [i], color='orange')

        ci_left.append((i, left))
        ci_right.append((i, right))
        ci_center.append((i, center))
        i += 1
    plt.plot([0, 0], [0, 30], color='red')
    plt.xlabel('ATE confidence interval')
    plt.ylabel('Team')
    plt.show()
    # (0.016442042958639658, -0.02024526584271785, 0.041451219237673)

if __name__ == '__main__':
    main()