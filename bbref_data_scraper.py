# import libs
import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path
import os
import sys

print('Running ', sys.argv[0])

months = sys.argv[2].strip('[]').split(',')
seasons = list(map(int, sys.argv[1].strip('[]').split(',')))

#hardcoded inputs for testing
#seasons = [2011, 2012, 2013, 2014, 2015, 2016, 2017]
#months = ['october', 'november', 'december', 'january', 'february', 'march', 'april', 'june']
for season in seasons: 
    print('Scraping data from the {s1}-{s2} NBA season'.format(s1=(season-1), s2=season))
    
    for month in months:
        
        # data extraction
        url = 'https://www.basketball-reference.com/leagues/NBA_{year}_games-{month}.html'
        scrape_url = url.format(year=season, month=month)
        
        r = requests.get(scrape_url)
        soup = BeautifulSoup(r.content, 'lxml')
        
        raw_results_box = soup.find('div', attrs={'id':'div_schedule'})
        #return to inner for-loop if there is no data for a given month
        if raw_results_box is None:
            continue
        else:
            raw_results = raw_results_box.text.strip()
        
        
        # basic data transformation
        row_results = raw_results.splitlines()
        
        row_results_cleansed = []
        
        for i in range(len(row_results)):
            if len(row_results[i]) > 25:
                row_data = row_results[i]
                row_data = row_data.replace(',', '')
                
                #normalizing date format
                if row_data[8].isdigit() and not row_data[9].isdigit():
                    row_data = row_data[:8] + '0' + row_data[8:]
               
                #normalizing time format
                if row_data[15].isdigit() and not row_data[16].isdigit():
                    row_data = row_data[:15] + '0' + row_data[15:]
                
                row_data = row_data[:15] + ' ' + row_data[15:20] + row_data[21:23] + ',' + row_data[23:]
                
                for j in range(22, len(row_data)+3, 1):
                    if row_data[j].isdigit() and not row_data[j-1].isdigit() and row_data[j-1] != ',' and row_data[j-1] != ' ':
                        row_data = row_data[:j] + ',' + row_data[j:]
                    if row_data[j-1].isdigit() and not row_data[j].isdigit() and row_data[j] != ',' and row_data[j:j+3] != 'ers':
                        row_data = row_data[:j] + ',' + row_data[j:]
                    
                for j in range(22, len(row_data), 1):
                    if row_data[j-9:j] == 'Box Score' and row_data[j:j+2] == 'OT':
                        row_data = row_data[:j] + ',1' + row_data[j+2:]
                    elif row_data[j-9:j] == 'Box Score' and row_data[j+3:j+5] == 'OT':
                        row_data = row_data[:j+3] + row_data[j+6:]
                    elif row_data[j-9:j] == 'Box Score':
                        row_data = row_data[:j] + ',0' + row_data[j:]
                
                if row_data[-1].isdigit():
                    row_data = row_data + ','
                row_results_cleansed.append(row_data.split(','))
        
        
        # writing data to csv
        dir_path = 'data/raw/' + scrape_url[45:53]
        directory = Path(dir_path)
        if not directory.exists():
            os.mkdir(directory)
        
        file_name = dir_path + '/' + scrape_url[54:-5] + '.csv'
        with open(file_name, 'w') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'Visitor', 'Visitor_PTS','Home', 'Home_PTS', 'Box Score', '#OTs', 'Attend.', 'Notes'])
            writer.writerows(row_results_cleansed)