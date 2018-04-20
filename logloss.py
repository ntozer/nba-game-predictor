from math import log
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPClassifier

def compute_logloss(p, y):
    """
    calculates the log loss for a set of predictions and labels
    N = number of data predictions to test
    p = list of predictions to test
    y = list of labels associated with the given predictions
    """
    logloss = 0
    N = len(p)
    try:
        for i in range(N):
            logloss = logloss - 1 / N * (y[i] * log(p[i]) + (1-y[i]) * log(1-p[i]))
    except IndexError:
        print('ERROR: Labels and Predictions are not both of the length N')
        return
    
    return logloss


def minimize_logloss(X_train, y_train, X_cval, y_cval, max_layers=4, max_perceptrons=50, min_layers=1, min_perceptrons=10, increment=1, perceptron_func='logistic'):
    min_logloss = 1
    hidden_layers = 0
    perceptrons = 0
    logloss_list = []
    layers_list = []
    perceptrons_list = []
    
    for i in range(min_layers, max_layers+1, 1):
        for j in range(min_perceptrons, max_perceptrons+1, increment):
            #setting up and training NN
            clf = MLPClassifier(solver='lbfgs', activation=perceptron_func, alpha=1e-5, hidden_layer_sizes=(j, i), random_state=1)
            clf.fit(X_train, y_train)
            
            #creating predicitons for cross val set
            p_cval = clf.predict_proba(X_cval)[:, 1].tolist()
            
            #computing logloss
            temp_logloss = compute_logloss(p_cval, y_cval)
            logloss_list.append(temp_logloss)
            layers_list.append(i)
            perceptrons_list.append(j)
            
            #checking for new logloss record
            if temp_logloss < min_logloss:
                min_logloss = temp_logloss
                hidden_layers = i
                perceptrons = j

    return (min_logloss, hidden_layers, perceptrons, logloss_list, layers_list, perceptrons_list)
                
def compute_stats(p_list, y_list):
    p = np.round_(p_list, 0)
    y = np.asarray(y_list)
    
    tp=0
    fn=0
    fp=0
    tn=0
    for i in range(len(y)):
        if p[i]==1 and y[i]==1:
            tp += 1
        elif p[i]==0 and y[i]==1:
            fn += 1
        elif p[i]==1 and y[i]==0:
            fp += 1
        elif p[i]==0 and y[i]==0:
            tn += 1
    precision = tp / (tp + fp) 
    recall = tp / (tp + tn)
    accuracy = (tp + tn)/(tp + fp + tn + fn)
    F1_score = 2 * (precision * recall)/(precision + recall)
    
    return (F1_score, precision, recall, accuracy)