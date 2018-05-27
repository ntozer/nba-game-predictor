import pandas as pd
from data_handler import load_raw_data


def main():
    seasons = list(range(2001, 2018))
    seasons_list = load_raw_data(seasons)
    seasons_list = clean_data(seasons_list)
    seasons_list = create_features(seasons_list, seasons)
    write_prepared_data(seasons_list, seasons)


def clean_data(df_list):
    """
    Params:
        df_list - list of dataframes with data to clean up
    Returns:
        df_list - returns list of dataframes with cleaned data
    """
    for idx in range(len(df_list)):
        #dropping unused rows
        df_list[idx] = df_list[idx].drop(['Notes', 'Box Score', '#OTs', 'Attend.'], axis=1)
        
        #splitting date column into list
        df_list[idx]['Day'] = df_list[idx]['Date'].str.split(' ').str[0]
        #converting day of the week to int
        day_di = {'Sun': 1, 'Mon': 2, 'Tue': 3, 'Wed': 4, 'Thu': 5, 'Fri': 6, 'Sat': 7}
        df_list[idx]['Day_Num'] = df_list[idx]['Date'].str.split(' ').str[0]
        df_list[idx]['Day_Num'].replace(day_di, inplace=True)
        #converting rest of date column to datetime type
        df_list[idx]['Date'] = pd.to_datetime(df_list[idx]['Date'])
        
        #calculating the spread of the home team and visitor team scores
        df_list[idx]['Spread'] = df_list[idx]['Home_PTS'] - df_list[idx]['Visitor_PTS']
        #creating a true/false column for whether or not the home team won
        df_list[idx]['Winner'] = df_list[idx]['Spread'] > 0
        #converting from boolean column to int
        winner_di = {True: 1, False: 0}
        df_list[idx]['Winner'].replace(winner_di, inplace=True)
        
    return df_list


def init_features(df):
    df['Home_TotalWins'] = 0
    df['Home_TotalLosses'] = 0
    df['Home_HomeWins'] = 0
    df['Home_HomeLosses'] = 0
    df['Home_Streak'] = 0
    df['Home_CumSpread'] = 0
    df['Home_AvgSpread'] = 0
    df['Home_CumPTS'] = 0
    df['Home_AvgPTS'] = 0
    df['Home_GamesPlayed'] = 0
    df['Home_DaysPast'] = 0
    df['Visitor_TotalWins'] = 0
    df['Visitor_TotalLosses'] = 0
    df['Visitor_VisitorWins'] = 0
    df['Visitor_VisitorLosses'] = 0
    df['Visitor_Streak'] = 0
    df['Visitor_CumSpread'] = 0
    df['Visitor_AvgSpread'] = 0
    df['Visitor_CumPTS'] = 0
    df['Visitor_AvgPTS'] = 0
    df['Visitor_GamesPlayed'] = 0
    df['Visitor_DaysPast'] = 0
    return df


def create_features(df_list, seasons=None):
    """
    Params:
        df_list - list of dataframes to add game by game features to
    """
    for i in range(len(df_list)):
        df = init_ELO(df_list, i)
        df = init_features(df)
        
        if seasons is not None:
            print('Creating features for the {} NBA season'.format(seasons[i]))
        
        
        for j, row in df.iterrows():
            
            teams = [(row['Home'], 'Home'), (row['Visitor'], 'Visitor')]
            for team in teams:
                team_name = team[0]
                game_type = team[1]
                
                (prev_game_idx, prev_game_type, prev_home_idx, prev_vis_idx)\
                    = find_prev_game(df[:j], team_name)

                if prev_game_idx != -1:
                    df = create_streak(df, j, game_type, prev_game_idx, prev_game_type)
                    df = create_record(df, j, game_type, prev_game_idx, prev_game_type)
                    df = create_ELO(df, j, game_type, prev_game_idx, prev_game_type)
                    df = create_pts_stats(df, j, game_type, prev_game_idx, prev_game_type)
                if prev_home_idx != -1:
                    if game_type == 'Home':
                        df = create_record(df, j, game_type, prev_home_idx, 'Home', False)
                if prev_vis_idx != -1:
                    if game_type == 'Visitor':
                        df = create_record(df, j, game_type, prev_vis_idx, 'Visitor', False)
        
        df = create_auxiliary_stats(df)
        df_list[i] = df
                    
    return df_list


def create_pts_stats(df, idx, game_type, prev_idx, prev_game_type):
    prev_tot_spread = df.loc[prev_idx, prev_game_type + '_CumSpread']
    prev_tot_pts = df.loc[prev_idx, prev_game_type + '_CumPTS']
    
    prev_spread = df.loc[prev_idx, 'Spread']
    if prev_game_type=='Visitor':
        prev_spread *= -1
    
    tot_spread = prev_tot_spread + prev_spread
    tot_pts = prev_tot_pts + df.loc[prev_idx, prev_game_type + '_PTS']
    
    df.loc[idx, game_type + '_CumSpread'] = tot_spread
    df.loc[idx, game_type + '_CumPTS'] = tot_pts
    
    return df

def create_record(df, idx, game_type, prev_idx, prev_game_type, general_rec=True):
    if general_rec:
        feature_name = '_Total'
    else:
        feature_name = '_' + game_type
        
    num_win = df.loc[prev_idx, prev_game_type + feature_name + 'Wins']
    num_loss = df.loc[prev_idx, prev_game_type + feature_name + 'Losses']    
        
    if won_game(df, prev_idx, prev_game_type):
        num_win += 1
    else:
        num_loss += 1
        
    df.loc[idx, game_type + feature_name + 'Wins'] = num_win
    df.loc[idx, game_type + feature_name + 'Losses'] = num_loss
 
    return df
    

def create_streak(df, idx, game_type, prev_idx, prev_game_type):
    curr_streak = df.loc[prev_idx, prev_game_type + '_Streak']
    
    if won_game(df, prev_idx, prev_game_type):
        if curr_streak >= 0:
            curr_streak += 1
        else:
            curr_streak = 1
    else:
        if curr_streak <= 0:
            curr_streak -= 1
        else:
            curr_streak = -1
    
    df.loc[idx, game_type + '_Streak'] = curr_streak
    
    return df


def init_ELO(df_list, idx):
    
    def soft_reset_ELO(prev_ELO):
        new_ELO = prev_ELO * 0.75 + (1505 * 0.25)
        return new_ELO
        
    df = df_list[idx]
    if idx == 0:
        df['Home_ELO'] = 1300
        df['Visitor_ELO'] = 1300
    else:
        df['Home_ELO'] = 1500
        df['Visitor_ELO'] = 1500
        prev_df = df_list[idx-1]
        i = 0
        teams = 0
        while teams < df['Home'].value_counts().size :
            #print(teams)
            home = df.loc[i, 'Home']
            vis = df.loc[i, 'Visitor']
            
            if not has_prev_game(df[:i], home):
                if has_prev_game(prev_df, home):
                    prev_idx, game_type, y, z = find_prev_game(prev_df, home)
                    df.loc[i, 'Home_ELO'] = soft_reset_ELO(prev_df.loc[prev_idx, game_type + '_ELO'])
                teams += 1

            if not has_prev_game(df[:i], vis):
                if has_prev_game(prev_df, vis):
                    prev_idx, game_type, y, z = find_prev_game(prev_df, vis)
                    df.loc[i, 'Visitor_ELO'] = soft_reset_ELO(prev_df.loc[prev_idx, game_type + '_ELO'])
                teams += 1
            
            i += 1

    return df

def create_ELO(df, idx, game_type, prev_idx, prev_game_type):
    winner = df.loc[prev_idx, 'Winner']
    won = False
    
    if prev_game_type == 'Home':
        opp_game_type = 'Visitor'
        if winner == 1:
            won = True      
    else:
        opp_game_type = 'Home'
        if winner == 0:
            won = True
    
    spread = df.loc[prev_idx, 'Spread']
    team_ELO = df.loc[prev_idx, prev_game_type + '_ELO']
    opp_ELO = df.loc[prev_idx, opp_game_type + '_ELO']
    
    updated_ELO = compute_ELO(team_ELO, opp_ELO, prev_game_type, won, spread)
    df.loc[idx, game_type + '_ELO'] = updated_ELO
    
    return df
    
def compute_ELO(team_ELO, opp_ELO, game_type, won, spread):
    """
    Implementation of Nate Silver's ELO formula
    """
    elo_diff = team_ELO - opp_ELO
    #accounting for homecourt advantage by reducing spread by 3 PTS
    if not won:
        S = 0
        elo_diff *= -1
        if game_type=='Home':
            spread *= -1
    else:
        S = 1
        if game_type=='Visitor':
            spread *= -1
    
    #computing estimated win probability
    E = 1 / (1 + 10 ** ((opp_ELO-team_ELO)/400))
    
    #computing K factor
    K = 20 * ((spread + 3)**0.8 / (7.5 + 0.006*elo_diff))

    #computing new elo
    updated_ELO = K * (S - E) + team_ELO
    
    return updated_ELO

def won_game(df, idx, game_type):
    """
    Params:
        df - dataframe with results
        idx - index to check for win @
        game_type - home/visitor for game
    Returns:
        bool - true if won, false if lost
    """
    if game_type=='Home' and df.loc[idx, 'Winner']==1:
        return True
    if game_type=='Visitor' and df.loc[idx, 'Winner']==0:
        return True
    return False

def create_auxiliary_stats(df):
    #computing total games played for home and away
    df['Home_GamesPlayed'] = df['Home_TotalWins'] + df['Home_TotalLosses']
    df['Visitor_GamesPlayed'] = df['Visitor_TotalWins'] + df['Visitor_TotalLosses']
    
    #computing avg total points
    df['Home_AvgSpread'] = df['Home_CumSpread'] / df['Home_GamesPlayed']
    df['Visitor_AvgSpread'] = df['Visitor_CumSpread'] / df['Visitor_GamesPlayed']
    df['Home_AvgSpread'] = df['Home_AvgSpread'].fillna(0)
    df['Visitor_AvgSpread'] = df['Visitor_AvgSpread'].fillna(0)
    
    #computing avg total pts
    df['Home_AvgPTS'] = df['Home_CumPTS'] / df['Home_GamesPlayed']
    df['Visitor_AvgPTS'] = df['Visitor_CumPTS'] / df['Visitor_GamesPlayed']
    df['Home_AvgPTS'] = df['Home_AvgPTS'].fillna(0)
    df['Visitor_AvgPTS'] = df['Visitor_AvgPTS'].fillna(0)
    
    return df


def has_prev_game(df, team):
    """
    Params:
        df - dataframe to locate prev game in
        team - name of the team to search for
    Returns:
        has_prev - boolean indicating whether there is a previous game
    """
    has_prev = ((df['Home']==team) | (df['Visitor']==team)).any()
    return has_prev

    
def find_prev_game(df, team):
    """
    Params:
        df - dataframe to locate prev game in
        team - name of the team to search for
    Returns:
        prev_game_idx - index of previous game (-1 if no prev game)
        game_type - home or visitor
        prev_home_idx - index of previous home game(-1 if no prev game)
        prev_vis_idx - index of previous visitor game(-1 if no prev game)
    """
    prev_game_idx = -1
    game_type = None
    
    if not has_prev_game(df, team):
        return (prev_game_idx, None, -1, -1)
    
    try:
        prev_home_idx = df.loc[df['Home']==team].index[-1]
    except IndexError:
        prev_home_idx = -1
    
    try:
        prev_vis_idx = df.loc[df['Visitor']==team].index[-1]
    except IndexError:
        prev_vis_idx = -1
    
    if prev_home_idx > prev_vis_idx:
        game_type = 'Home'
        prev_game_idx = prev_home_idx
    else:
        game_type = 'Visitor'
        prev_game_idx = prev_vis_idx
    
    return (prev_game_idx, game_type, prev_home_idx, prev_vis_idx)


def write_prepared_data(df_list, seasons):
    """
    Params:
        df_list - list of dataframes to write out
        seasons - year of seasons to write out
    """
    for i in range(len(df_list)):
        print('Writing prepared data to /data/prep/{s}_NBAseason.csv'.format(s=seasons[i]))
        df_list[i].to_csv('data/prep/{s}_NBAseason.csv'.format(s=seasons[i]))


if __name__ == "__main__":
    main()