"""Import LA County Covid-19 data from NY Times Github and write to .csv"""

# NY Times COVID-19 data with rolling averages can be found at: 
# https://github.com/nytimes/covid-19-data/tree/master/rolling-averages 
# (as of 2022-04-01). The data is split between .csv files by year.

import urllib.request
import numpy as np
import pandas as pd
import logging
import os

# Download data

url_dict = {
    2020: 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us-counties-2020.csv',
    2021: 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us-counties-2021.csv',
    2022: 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us-counties-2022.csv',
}

# Log downloads
log_dir = 'logs'
log_fname = 'log.log'

# Create and configure logger
logging.basicConfig(
    filename=os.path.join(log_dir, log_fname),
    format='%(asctime)s %(message)s',
    filemode='w'
)

# Create object
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

for year in url_dict:
    try:
        print(f'Starting download of {year} data...')
        logger.info(f'Starting download of {year} data...')
        url = url_dict[year]
        output = f'us-counties-{year}.csv'
        urllib.request.urlretrieve(url, output)
        print(f'{year} data saved.')
        logger.info(f'{year} data saved.')
    except Exception as e:
        print(f'Error downloading {year} data file: {str(e)}')
        logger.error(f'Error downloading {year} data file: {str(e)}')
        
# Load data

df_dict = {year: pd.read_csv(f'us-counties-{year}.csv') for year in url_dict}

# Extract LA County data
la_df_dict = {year: df.loc[(df['county'] == 'Los Angeles') & (df['state'] == 'California')] for year, df in df_dict.items()}

# Combine into one DataFrame
la_df = pd.concat(
    la_df_dict
).reset_index(
).drop(
    columns=['level_0', 'level_1']
)

# Export data to .csv for use downstream

la_df.to_csv('los_angeles_covid_cases.csv', index=False)