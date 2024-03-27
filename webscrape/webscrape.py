import requests
from bs4 import BeautifulSoup
import pandas as pd
import modules.query as q
from sqlalchemy import create_engine

    
username = 'eric'
password = 'nomeat555'
host = '96.38.123.26'  # or your host, e.g., '127.0.0.1'
database = 'basketballstats'



def getTable():
# URL of the NBA players statistics page on Basketball-Reference
    url = 'https://www.basketball-reference.com/leagues/NBA_2024_per_game.html'

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
        

        # Create a MySQL engine
        engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}/{database}')

        df.to_sql('stats_23-24', con=engine, if_exists='replace', index=False)

# def scrape_image_url(player_url):
#     response = requests.get(player_url)
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.content, 'html.parser')
#         og_image_tag = soup.find("meta", property="og:image")
#         if og_image_tag:
#             return og_image_tag["content"]
#     return None

def add_image():
    url = 'https://www.basketball-reference.com/leagues/NBA_2024_per_game.html'

# Send a GET request to the URL
    response = requests.get(url)
    #print(response.status_code)
# Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the table containing player statistics
        table = soup.find('table', {'id': 'per_game_stats'})
        
        # Iterate through each row of the table
        rows = table.find_all('tr')[1:]  # Skip the header row
        for row in rows:
            # Find player name
            player_name_elem = row.find('td', {'data-stat': 'player'})
            if player_name_elem:
                player_name = player_name_elem.text
                player_link = row.find('td', {'data-stat': 'player'}).find('a')['href']
                player_id = player_link.split("/")[-1].split(".")[0]
                image_url = 'https://www.basketball-reference.com/req/202106291/images/headshots/' + player_id + '.jpg'
            else:
                player_name = None
                image_url = None
            print(player_name)
            
            conn = q.connect_to_database()
            sql_query = f"""UPDATE basketballstats.stats_23_24 
                SET image_url = '{image_url}'
                WHERE player = "{player_name}" AND image_url IS NULL """
            
            cursor = conn.cursor()
            cursor.execute(sql_query)
            conn.commit()
            cursor.close()
            conn.close()
            #print(image_url)

    else:
        print("failure")


def getLineScore(): 
    url = "https://www.basketball-reference.com/boxscores/?month=03&day=19&year=2024"
    response = requests.get(url)
    #print(response.status_code)
# Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')
        td_elements = soup.find_all('td', class_='center')
        counter = 0

        for td in td_elements:
            
            if counter % 4 == 0:
                counter = 0
                previous = td.find_previous_sibling()
                previous_href = previous.find('a')['href']
                team = previous_href.split('teams/')[-1].split('/')[0]
                print(team)

            counter += 1
            score = td.get_text(strip=True)
            quarter = f"q{counter}_teamScoring"
            conn = q.connect_to_database()
            sql_query = f"""UPDATE basketballstats.last_5_games
                            SET {quarter} = "{score}"
                            WHERE Date = "2024-03-19" 
                            AND Team = "{team}" AND {quarter} IS NULL"""
            
            cursor = conn.cursor()
            cursor.execute(sql_query)
            conn.commit()
            cursor.close()
            conn.close()
            print(quarter, score)
            
        