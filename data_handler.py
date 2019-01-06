import pandas as pd
import numpy as np


class DataHandler:
    def __init__(self):
        self.dataset = None

    def load_dataset(self, seasons, path):
        df = None
        for season in seasons:
            try:
                temp_df = pd.read_csv(f'{path}/NBA_{season}.csv')
                if df is None:
                    df = temp_df
                else:
                    df = df.append(temp_df, ignore_index=True)
            except FileNotFoundError:
                print(f'ERROR: {path}/NBA_{season}.csv not found')

        self.dataset = df

    def split_dataset(self, ratios):
        msk = np.random.rand(len(self.dataset)) < ratios[0]
        train = self.dataset[msk]
        test_val = self.dataset[~msk]
        msk = np.random.rand(len(test_val)) < (ratios[1] / (ratios[1] + ratios[2]))
        val = test_val[msk]
        test = test_val[~msk]
        return train, val, test
