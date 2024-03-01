import requests
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine


# Get the active player ids
def scrape_active_player_ids():
    base_url = 'https://www.basketball-reference.com/players/'
    active_player_ids = []
    # Basketball-Reference has pages for players sorted by the first letter of their surname
    for letter in 'abcdefghijklmnopqrstuvwxyz':
        response = requests.get(f'{base_url}{letter}/')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Find all player links; active players are in bold
            for player in soup.find_all('strong'):
                link = player.find('a')
                if link and 'href' in link.attrs:
                    player_id = link.attrs['href'].split('/')[3].replace('.html', '')
                    active_player_ids.append(player_id)
    return active_player_ids


# Function to get the last 5 games for a single player
def get_last_5_games(player_id):
    url = f'https://www.basketball-reference.com/players/{player_id}/gamelog/2024'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'id': 'pgl_basic'})  # Adjust if the table ID is different
        player_data = []
        if table:  # Check if the table is found
            rows = table.find('tbody').find_all('tr')[-5:]  # Get the last 5 rows for the games
            for row in rows:
                if 'thead' not in row.get('class', []):  # This filters out header rows in the data
                    player_row = [td.text.strip() for td in row.find_all(['th', 'td'])]
                    player_data.append(player_row)
        return player_data
    return []


player_ids = scrape_active_player_ids()

# Initialize an empty list to store all players' data
all_players_data = []


# Column headers, adjust according to the actual table you're scraping
headers = ['Player', 'Date', 'Opp', 'Result', 'GS', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', '+/-']
print("HERE")

for player_id in player_ids:
    player_games = get_last_5_games(player_id)
    for game in player_games:
        all_players_data.append([player_id] + game)  # Add player ID to each game data


# Convert the list of player data into a DataFrame
df = pd.DataFrame(all_players_data, columns=headers)


# Database connection parameters

username = 'eric'
password = 'nomeat555'
host = '96.38.123.26'  # or your host, e.g., '127.0.0.1'
database = 'basketballstats'

# Create a MySQL engine
engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}/{database}')


# Save the DataFrame to SQL
df.to_sql('last_5_games', con=engine, if_exists='replace', index=False)