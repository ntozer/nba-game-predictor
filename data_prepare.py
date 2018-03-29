# standard imports
import pandas as pd
import sys

print('Running ', sys.argv[0])

seasons = list(map(int, sys.argv[1].strip('[]').split(',')))
months = sys.argv[2].strip('[]').split(',')

#read in data
for season in seasons:
    df = None
    
    print('Processing data for the {s1}-{s2} NBA season'.format(s1=(season-1), s2=season))
    
    for month in months:
        try:
            temp_df = pd.read_csv('data/raw/NBA_{s}/games-{m}.csv'.format(s=season, m=month))
            if df is None:
                df = temp_df
            else:
                df = df.append(temp_df, ignore_index=True)
        except FileNotFoundError:
            print('No data for month of ', month)
            continue
    #dropping unused rows
    df = df.drop(['Notes', 'Box Score', '#OTs', 'Attend.'], axis=1)
    
    #splitting date column into list
    df['Day'] = df['Date'].str.split(' ').str[0]
    #converting day of the week to int
    day_di = {'Sun': 1, 'Mon': 2, 'Tue': 3, 'Wed': 4, 'Thu': 5, 'Fri': 6, 'Sat': 7}
    df['Day_Num'] = df['Date'].str.split(' ').str[0]
    df['Day_Num'].replace(day_di, inplace=True)
    #converting rest of date column to datetime type
    df['Date'] = pd.to_datetime(df['Date'])
    
    #calculating the spread of the home team and visitor team scores
    df['Spread'] = df['Home_PTS'] - df['Visitor_PTS']
    #creating a true/false column for whether or not the home team won
    df['Winner'] = df['Spread'] > 0
    #converting from boolean column to int
    winner_di = {True: 1, False: 0}
    df['Winner'].replace(winner_di, inplace=True)
    
    #creating 0 columns for desired features
    df['Home_TotalWins'] = 0
    df['Home_TotalLosses'] = 0
    df['Home_HomeWins'] = 0
    df['Home_HomeLosses'] = 0
    df['Home_Streak'] = 0
    df['Home_CumSpread'] = 0
    df['Home_AvgSpread'] = 0
    df['Home_CumPts'] = 0
    df['Home_AvgPts'] = 0
    df['Home_GamesPlayed'] = 0
    df['Home_DaysPast'] = 0
    df['Visitor_TotalWins'] = 0
    df['Visitor_TotalLosses'] = 0
    df['Visitor_VisitorWins'] = 0
    df['Visitor_VisitorLosses'] = 0
    df['Visitor_Streak'] = 0
    df['Visitor_CumSpread'] = 0
    df['Visitor_AvgSpread'] = 0
    df['Visitor_CumPts'] = 0
    df['Visitor_AvgPts'] = 0
    df['Visitor_GamesPlayed'] = 0
    df['Visitor_DaysPast'] = 0
    
    for index, row in df.iterrows():
        #checking for if there are any previous games up to the index value for the home team
        if ((df[:index]['Home']==row['Home']) | (df[:index]['Visitor']==row['Home'])).any():
            #getting the idx of the home team's last home game
            try:
                last_home_idx = df[:index].loc[df['Home']==row['Home']].index[-1]
                
                #updating home team's home record
                if df.loc[last_home_idx, 'Winner'] == 1:
                    df.loc[index, 'Home_HomeWins'] = df.loc[last_home_idx, 'Home_HomeWins'] + 1
                    df.loc[index, 'Home_HomeLosses'] = df.loc[last_home_idx, 'Home_HomeLosses']
                else:
                    df.loc[index, 'Home_HomeWins'] = df.loc[last_home_idx, 'Home_HomeWins']
                    df.loc[index, 'Home_HomeLosses'] = df.loc[last_home_idx, 'Home_HomeLosses'] + 1
            except IndexError:
                last_home_idx = -1
            
            #getting the idx of the home team's last visitor game
            try:
                last_visitor_idx = df[:index].loc[df['Visitor']==row['Home']].index[-1]
            except IndexError:
                last_visitor_idx = -1
            
            #checking if the home team's last game was an away or home game
            if last_home_idx > last_visitor_idx:
                #updating record when last game was home game
                prev_index = last_home_idx
                if df.loc[prev_index, 'Winner'] == 1:
                    df.loc[index, 'Home_TotalWins'] = df.loc[prev_index, 'Home_TotalWins'] + 1
                    df.loc[index, 'Home_TotalLosses'] = df.loc[prev_index, 'Home_TotalLosses']
                    
                    #updating streak
                    if df.loc[prev_index, 'Home_Streak'] >= 0:
                        df.loc[index, 'Home_Streak'] = df.loc[prev_index, 'Home_Streak'] + 1
                    else:
                        df.loc[index, 'Home_Streak'] = 1
                        
                else:
                    df.loc[index, 'Home_TotalWins'] = df.loc[prev_index, 'Home_TotalWins']
                    df.loc[index, 'Home_TotalLosses'] = df.loc[prev_index, 'Home_TotalLosses'] + 1
                    
                    #updating streak
                    if df.loc[prev_index, 'Home_Streak'] <= 0:
                        df.loc[index, 'Home_Streak'] = df.loc[prev_index, 'Home_Streak'] - 1
                    else:
                        df.loc[index, 'Home_Streak'] = -1
                
                #updating spread for home team
                df.loc[index, 'Home_CumSpread'] = df.loc[prev_index, 'Home_CumSpread'] + df.loc[prev_index, 'Spread']
                #updating season pts for home team
                df.loc[index, 'Home_CumPts'] = df.loc[prev_index, 'Home_CumPts'] + df.loc[prev_index, 'Home_PTS']
                #updating days since last game
                df.loc[index, 'Home_DaysPast'] = (df.loc[index, 'Date'] - df.loc[prev_index, 'Date']).total_seconds() / (60 * 60 * 24)
                
                        
            else:
                #updating record when last game was away game
                prev_index = last_visitor_idx
                if df.loc[prev_index, 'Winner'] == 0:
                    df.loc[index, 'Home_TotalWins'] = df.loc[prev_index, 'Visitor_TotalWins'] + 1
                    df.loc[index, 'Home_TotalLosses'] = df.loc[prev_index, 'Visitor_TotalLosses']
                    
                    #updating streak
                    if df.loc[prev_index, 'Visitor_Streak'] >= 0:
                        df.loc[index, 'Home_Streak'] = df.loc[prev_index, 'Visitor_Streak'] + 1
                    else:
                        df.loc[index, 'Home_Streak'] = 1
                        
                else:
                    df.loc[index, 'Home_TotalWins'] = df.loc[prev_index, 'Visitor_TotalWins']
                    df.loc[index, 'Home_TotalLosses'] = df.loc[prev_index, 'Visitor_TotalLosses'] + 1
                    
                    #updating streak
                    if df.loc[prev_index, 'Visitor_Streak'] <= 0:
                        df.loc[index, 'Home_Streak'] = df.loc[prev_index, 'Visitor_Streak'] - 1
                    else:
                        df.loc[index, 'Home_Streak'] = -1
                    
                #updating spread for home team
                df.loc[index, 'Home_CumSpread'] = df.loc[prev_index, 'Visitor_CumSpread'] - df.loc[prev_index, 'Spread']
                #updating season pts for home team
                df.loc[index, 'Home_CumPts'] = df.loc[prev_index, 'Visitor_CumPts'] + df.loc[prev_index, 'Visitor_PTS']
                #updating days since last game
                df.loc[index, 'Home_DaysPast'] = (df.loc[index, 'Date'] - df.loc[prev_index, 'Date']).total_seconds() / (60 * 60 * 24)
            
        #checking for if there are any previous games up to the index value for the visitor team    
        if ((df[:index]['Home']==row['Visitor']) | (df[:index]['Visitor']==row['Visitor'])).any():   
            
            #getting the index of the visitor's last home game
            try:
                last_home_idx = df[:index].loc[df['Home']==row['Visitor']].index[-1]
            except IndexError:
                last_home_idx = -1
                
            #getting the index of the visitor's last away game
            try:
                last_visitor_idx = df[:index].loc[df['Visitor']==row['Visitor']].index[-1]
                
                #updating the visiting team's visitor record
                if df.loc[last_visitor_idx, 'Winner'] == 0:
                    df.loc[index, 'Visitor_VisitorWins'] = df.loc[last_visitor_idx, 'Visitor_VisitorWins'] + 1
                    df.loc[index, 'Visitor_VisitorLosses'] = df.loc[last_visitor_idx, 'Visitor_VisitorLosses']
                else:
                    df.loc[index, 'Visitor_VisitorWins'] = df.loc[last_visitor_idx, 'Visitor_VisitorWins'] 
                    df.loc[index, 'Visitor_VisitorLosses'] = df.loc[last_visitor_idx, 'Visitor_VisitorLosses'] + 1
                
            except IndexError:
                last_visitor_idx = -1
                
            #checking if the visitor team's last game was an away or home game
            if last_home_idx > last_visitor_idx:
                #updating record when last game was home game
                prev_index = last_home_idx
                if df.loc[prev_index, 'Winner'] == 1:
                    df.loc[index, 'Visitor_TotalWins'] = df.loc[prev_index, 'Home_TotalWins'] + 1
                    df.loc[index, 'Visitor_TotalLosses'] = df.loc[prev_index, 'Home_TotalLosses']
                    
                    #updating streak
                    if df.loc[prev_index, 'Home_Streak'] >= 0:
                        df.loc[index, 'Visitor_Streak'] = df.loc[prev_index, 'Home_Streak'] + 1
                    else:
                        df.loc[index, 'Visitor_Streak'] = 1
                    
                else:
                    df.loc[index, 'Visitor_TotalWins'] = df.loc[prev_index, 'Home_TotalWins']
                    df.loc[index, 'Visitor_TotalLosses'] = df.loc[prev_index, 'Home_TotalLosses'] + 1
                    
                    #updating streak
                    if df.loc[prev_index, 'Home_Streak'] <= 0:
                        df.loc[index, 'Visitor_Streak'] = df.loc[prev_index, 'Home_Streak'] - 1
                    else:
                        df.loc[index, 'Visitor_Streak'] = -1
                
                #updating spread for visitor team
                df.loc[index, 'Visitor_CumSpread'] = df.loc[prev_index, 'Home_CumSpread'] + df.loc[prev_index, 'Spread']
                #updating season pts for home team
                df.loc[index, 'Visitor_CumPts'] = df.loc[prev_index, 'Home_CumPts'] + df.loc[prev_index, 'Home_PTS']
                #updating days since last game
                df.loc[index, 'Visitor_DaysPast'] = (df.loc[index, 'Date'] - df.loc[prev_index, 'Date']).total_seconds() / (60 * 60 * 24)
                
            else:
                #updating record when last game was away game
                prev_index = last_visitor_idx
                if df.loc[prev_index, 'Winner'] == 0:
                    df.loc[index, 'Visitor_TotalWins'] = df.loc[prev_index, 'Visitor_TotalWins'] + 1
                    df.loc[index, 'Visitor_TotalLosses'] = df.loc[prev_index, 'Visitor_TotalLosses']
                    
                    #updating streak
                    if df.loc[prev_index, 'Visitor_Streak'] >= 0:
                        df.loc[index, 'Visitor_Streak'] = df.loc[prev_index, 'Visitor_Streak'] + 1
                    else:
                        df.loc[index, 'Visitor_Streak'] = 1
                    
                else:
                    df.loc[index, 'Visitor_TotalWins'] = df.loc[prev_index, 'Visitor_TotalWins']
                    df.loc[index, 'Visitor_TotalLosses'] = df.loc[prev_index, 'Visitor_TotalLosses'] + 1
                    
                    #updating streak
                    if df.loc[prev_index, 'Visitor_Streak'] <= 0:
                        df.loc[index, 'Visitor_Streak'] = df.loc[prev_index, 'Visitor_Streak'] - 1
                    else:
                        df.loc[index, 'Visitor_Streak'] = -1
                
                #updating spread for visitor team
                df.loc[index, 'Visitor_CumSpread'] = df.loc[prev_index, 'Visitor_CumSpread'] - df.loc[prev_index, 'Spread']
                #updating season pts for home team
                df.loc[index, 'Visitor_CumPts'] = df.loc[prev_index, 'Visitor_CumPts'] + df.loc[prev_index, 'Visitor_PTS']
                #updating days since last game
                df.loc[index, 'Visitor_DaysPast'] = (df.loc[index, 'Date'] - df.loc[prev_index, 'Date']).total_seconds() / (60 * 60 * 24)
    
    #computing total games played for home and away
    df['Home_GamesPlayed'] = df['Home_TotalWins'] + df['Home_TotalLosses']
    df['Visitor_GamesPlayed'] = df['Visitor_TotalWins'] + df['Visitor_TotalLosses']
    
    #computing avg total points
    df['Home_AvgSpread'] = df['Home_CumSpread'] / df['Home_GamesPlayed']
    df['Visitor_AvgSpread'] = df['Visitor_CumSpread'] / df['Visitor_GamesPlayed']
    df['Home_AvgSpread'] = df['Home_AvgSpread'].fillna(0)
    df['Visitor_AvgSpread'] = df['Visitor_AvgSpread'].fillna(0)
    
    #computing avg total pts
    df['Home_AvgPts'] = df['Home_CumPts'] / df['Home_GamesPlayed']
    df['Visitor_AvgPts'] = df['Visitor_CumPts'] / df['Visitor_GamesPlayed']
    df['Home_AvgPts'] = df['Home_AvgPts'].fillna(0)
    df['Visitor_AvgPts'] = df['Visitor_AvgPts'].fillna(0)
    
    df.to_csv('data/prepared/{s}_NBAseason.csv'.format(s=season))