from math import log
import matplotlib.pyplot as plt

def compute_logloss(N, p, y):
    """
    calculates the log loss for a set of predictions and labels
    N = number of data predictions to test
    p = list of predictions to test
    y = list of labels associated with the given predictions
    """
    logloss = 0
    try:
        for i in range(N):
            logloss = logloss - 1 / N * (y[i] * log(p[i]) + (1-y[i]) * log(1-p[i]))
    except IndexError:
        print('ERROR: Labels and Predictions are not both of the length N')
        return
    
    return logloss

def create_logloss_subplot(N, p, y):
    """
    graphs the log loss over the iterations of prediction/label pairs
    N = number of data predictions to test
    p = list of predictions to test
    y = list of labels associated with the given predictions
    """
    logloss_list = []
    try:
        for i in range(N):
            logloss_list.append(compute_logloss(N, p, y))
    except IndexError:
        print('ERROR: Labels and Predictions are not both of the length N')
        return
    
    fig = plt.figure()
    fig.add_axes()
    ax = fig.add_subplot(111)
    ax.plot(range(len(logloss_list)), logloss_list)
    
    return ax
        