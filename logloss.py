from math import log
import numpy as np
from sklearn.neural_network import MLPClassifier

def compute_logloss(p, y):
    """
    calculates the log loss for a set of predictions and labels
    Params:
        p - list of predictions to test
        y - list of labels associated with the given predictions
    Returns:
        logloss - the logloss of the predictions
    """
    logloss = 0
    N = len(p)
    eps = 1e-15
    try:
        for i in range(N):
            logloss = logloss - 1 / N * (y[i] * log(p[i]+eps) + (1-y[i]) * log(1-p[i]+eps))
    except IndexError:
        print('ERROR: Labels and Predictions are not both of the length N')
        return
    
    return logloss


def minimize_logloss(X_train, y_train, X_cval, y_cval, max_layers=4, max_perceptrons=50, min_layers=1, min_perceptrons=10, increment=1, perceptron_func='logistic'):
    """
    determines the optimal Deep Neural Network size through optimizing for minimum logloss on the cross validation set
    Params:
        X_train - the training feature set
        y_train - the training label set
        X_cval - the cross validation feature set
        y_cval - the cross validation label set
        max_layers - maximum number of layers to test with
        max_perceptron - maximum number of perceptrons to test with
        min_layers -  minimum number of layers to test with
        min_perceptrons - minimum number of perceptrons to test with
        increment - number of perceptrons to increment by for each test, layers always increment by 1
        perceptron_func - the activation function of the perceptrons(options: 'identity', 'logistic', 'tanh', 'relu')
    Returns:
        min_logloss - optimal logloss value found on the cross validation set
        hidden_layers - optimal number of layers
        perceptrons - optimal number of perceptrons
        logloss_list - a list of all logloss values associated with each tested layer perceptron combination
        layers_list - a list of all tested layer values
        perceptrons_list - a list of all tested perceptron values
    """
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
    """
    Params:
        p_list - list of prediction values
        y_list - list of labels associated with predictions
    Returns:
        F1_score - the F1 score based on the predictions and labels
        Precision - the precision based of hte predictions
        Recall - the recall based on the predictions
        Accuracy - the accuracy based on the predictions
    """
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