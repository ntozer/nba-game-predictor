@echo off

set months=[october,november,december,january,february,march,april,may,june]
set years=[2008,2009,2010]

cd %~dp0

python bbref_data_scraper.py %years% %months%
python data_prepare.py %years% %months%

echo Data scraping and preparation complete