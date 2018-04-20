import matplotlib.pyplot as plt
import pandas as pd
from logloss import compute_logloss


def viz_feature_2d(df, home_feature, visitor_feature):
    """
    Params:
        df - dataframe where the features and labels are contained
        home_feature - name of the feature for the home team
        visitor_feature - name of the feature for the visitor team
    """
    win_df = df[df['Winner'] == 1]
    loss_df = df[df['Winner'] == 0]
    
    fig, ax = plt.subplots(1, 1)
    
    ax.scatter(win_df[visitor_feature].tolist(), win_df[home_feature].tolist(), marker='o', c='y', edgecolor='face', label='Home Win')
    ax.scatter(loss_df[visitor_feature].tolist(), loss_df[home_feature].tolist(), marker='x', c='r', label='Visitor Win')
    
    plt.xlabel(visitor_feature)
    plt.ylabel(home_feature)
    
    plt.legend(loc='upper left')
    
    plt.show()
    

def viz_logloss(p, y):
    """
    graphs the log loss over the iterations of prediction/label pairs
    Params:
        N = number of data predictions to test
        p = list of predictions to test
        y = list of labels associated with the given predictions
    """
    logloss_list = []
    N = len(p)
    try:
        for i in range(N):
            logloss_list.append(compute_logloss(p[:i], y[:i]))
    except IndexError:
        print('ERROR: Labels and Predictions are not both of the length N')
        return
    
    fig = plt.figure()
    fig.add_axes()
    ax = fig.add_subplot(111)
    ax.plot(range(len(logloss_list)), logloss_list)
    
    plt.ylabel('Logloss')
    plt.xlabel('Number of Games Analyzed')
    
    plt.show()