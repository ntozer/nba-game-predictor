import pandas as pd
import numpy as np


def load_prep_data(seasons):
    df = None
    for season in seasons:
        try:
            temp_df = pd.read_csv('data/prep/{}_NBAseason.csv'.format(season))
            if df is None:
                df = temp_df
            else:
                df = df.append(temp_df, ignore_index=True)
        except FileNotFoundError:
            print('ERROR: data/prep/{}_NBAseason.csv not found'.format(season))
    
    return df


def seperate_dataset(df):
    """
    Params:
        df - dataframe to split into train, cross val., and test sets
    Returns:
        train - training dataset
        cval - cross validation dataset
        test - testing dataset
    """
    msk = np.random.rand(len(df)) < 0.6
    train = df[msk]
    test_cval = df[~msk]
    msk = np.random.rand(len(test_cval)) < 0.5
    cval = test_cval[msk]
    test = test_cval[~msk]
    
    return(train, cval, test)