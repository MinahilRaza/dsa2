# -*- coding: utf-8 -*-
"""PastClick_Duration

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JCctCDQY8EwO5lfAEhAcp_mssPmr5udg
"""

import pandas as pd
import numpy as np

dtypes = {'ip': np.uint32, 'app': np.uint16, 'device': np.uint8, 'os': np.uint8, 'channel': np.uint8, 'is_attributed': np.bool}
df = pd.read_csv('raw/train_100k.csv', sep=',', dtype=dtypes, parse_dates=['click_time', 'attributed_time'])
df.head()

def generateAggregateFeatures(df, aggregateFeatures):
    for spec in aggregateFeatures:
        print("Generating aggregate feature {} group by {}, and aggregating {} with {}".format(spec['name'], spec['groupBy'], spec['select'], spec['agg']))
        gp = df[spec['groupBy'] + [spec['select']]] \
            .groupby(by=spec['groupBy'])[spec['select']] \
            .agg(spec['agg']) \
            .reset_index() \
            .rename(index=str, columns={spec['select']: spec['name']})
        df = df.merge(gp, on=spec['groupBy'], how='left')
        del gp
        gc.collect()
     
    return df

aggregateFeatures = [
    # How popular is the app in channel?
    {'name': 'app-popularity', 'groupBy': ['app'], 'select': 'channel', 'agg': 'count'},
    # How popular is the channel in app?
    {'name': 'channel-popularity', 'groupBy': ['channel'], 'select': 'app', 'agg': 'count'},
    # Average clicks on app by distinct users; is it an app they return to?
    {'name': 'avg-clicks-on-app', 'groupBy': ['app'], 'select': 'ip', 'agg': lambda x: float(len(x)) / len(x.unique())}
]
df = generateAggregateFeatures(df, aggregateFeatures)
df.head()

# Time between past clicks
def generatePastClickFeatures(df, pastClickAggregateFeatures):
    for spec in pastClickAggregateFeatures:
        feature_name = '{}-past-click'.format('_'.join(spec['groupBy']))   
        df[feature_name] = df[spec['groupBy'] + ['click_time']].groupby(['ip']).click_time.transform(lambda x: x.diff().shift(1)).dt.seconds
    return df

pastClickAggregateFeatures = [
    {'groupBy': ['ip', 'channel']},
    {'groupBy': ['ip', 'os']}
]

df = generatePastClickFeatures(df, pastClickAggregateFeatures)
df.head()
