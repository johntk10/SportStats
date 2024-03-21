import requests
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine
import time

# Function to get the last 5 games for a single player
def get_last_5_games(player_id):
    #https://www.basketball-reference.com/players/a/achiupr01.html
    url = f'https://www.basketball-reference.com/players/{player_id[0]}/{player_id}.html'
    print(url)
    #url = f'https://www.basketball-reference.com/players/{player_id}/gamelog/2024'
    response = requests.get(url)
    time.sleep(3)
    print(response.status_code)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'id': 'last5'})
        player_data = []
        if table:  # Check if the table is found
            # Get the last 5 rows for the games
            rows = table.find('tbody').find_all('tr')
            for row in rows:
                # Extracting data from each cell
                player_row = [td.get_text(strip=True) for td in row.find_all(['th', 'td'])]
                player_data.append(player_row)
        return player_data
    return []

# Initialize an empty list to store all players' data
all_players_data = []

# Column headers, adjust according to the actual table you're scraping
headers = ['Player', 'Date', 'Team', '@', 'Opp', 'Result', 'GS', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'GmSc', '+/-']
print(len(headers))

player_ids = []
with open('active_player_ids.txt', 'r') as file:  # Ensure the file is named 'player_ids.txt' and located in the correct directory
    player_ids = [line.strip() for line in file.readlines()]

#print(player_ids)

for player_id in player_ids:
    player_games = get_last_5_games(player_id)
    #print(player_games)
    for game in player_games:
        all_players_data.append([player_id] + game)  # Add player ID to each game data
        print(all_players_data)
print(all_players_data)

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