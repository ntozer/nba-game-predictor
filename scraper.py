import requests
import pandas as pd
import lxml.html as lh


class Scraper:
    def __init__(self, seasons, months=['october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june']):
        self.seasons = seasons
        self.months = months

    def fetch_bbref_game_data(self):
        season_dfs = {}
        col_names = ['Date', 'Time', 'Visitor', 'Vis_PTS','Home', 'Home_PTS', 'Box Score', '#OTs', 'Attend.', 'Notes']
        for season in self.seasons:
            df = None
            for month in self.months:
                url = f'https://www.basketball-reference.com/leagues/NBA_{season}_games-{month}.html'
                page = requests.get(url=url)
                if page.status_code != 200:
                    print(f'Response {page.status_code} for NBA {season-1}-{season}: {month}')
                    continue
                doc = lh.fromstring(page.content)
                tr_elements = doc.xpath('//tr')

                col = []
                for i in range(len(tr_elements[0])):
                    col.append((col_names[i], []))

                for i in range(1, len(tr_elements)):
                    T = tr_elements[i]
                    if len(T) != 10:
                        continue

                    j = 0
                    for t in T.iterchildren():
                        data = t.text_content()

                        try:
                            data = int(data)
                        except ValueError:
                            pass

                        col[j][1].append(data)
                        j += 1

                df_dict = {title: column for (title, column) in col}
                try:
                    df.append(pd.DataFrame(df_dict))
                except AttributeError:
                    df = pd.DataFrame(df_dict)
            season_dfs[season] = df
        return season_dfs

