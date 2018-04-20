import pandas as pd
import numpy as np


def load_raw_data(seasons, months=['october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june']):
    """
    Params:
        seasons - the seasons to load data from
        months - the months to load data from
    Returns:
        df_list - list containing a dataframe for each season loaded
    """
    df_list = []
    for season in seasons:
        print('Loading raw data from /data/raw/NBA_{s}/[months].csv'.format(s=season))
        df = None
        for month in months:
            try:
                temp_df = pd.read_csv('data/raw/NBA_{s}/games-{m}.csv'.format(s=season, m=month))
                if df is None:
                    df = temp_df
                else:
                    df = df.append(temp_df, ignore_index=True)
            except FileNotFoundError:
                print('No data for month of', month)
                continue
                
        df_list.append(df)
    
    return df_list


def load_prep_data(seasons):
    """
    Params:
        seasons - the seasons from which to load data
    Returns:
        df - dataframe containing the seasons games
    """
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