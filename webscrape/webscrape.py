import requests
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine

# URL of the NBA players statistics page on Basketball-Reference
url = 'https://www.basketball-reference.com/leagues/NBA_2022_per_game.html'

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the table containing player statistics
    table = soup.find('table', {'id': 'per_game_stats'})
    
    # Extract column headers
    headers = [th.text.strip() for th in table.find('thead').find_all('th')]
    
    # Initialize an empty list to store player data
    player_data = []
    
    # Iterate over rows in the table body
    for row in table.find('tbody').find_all('tr'):
        # Extract data from each cell in the row
        player_row = [td.text.strip() for td in row.find_all(['th', 'td'])]
        # Add player data to the list
        player_data.append(player_row)
    
    # Convert the list of player data into a DataFrame
    df = pd.DataFrame(player_data, columns=headers)
    
    username = 'eric'
    password = 'nomeat555'
    host = 'localhost'  # or your host, e.g., '127.0.0.1'
    database = 'killjohn'

    # Create a MySQL engine
    engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}/{database}')

    df.to_sql('stats', con=engine, if_exists='replace', index=False)
