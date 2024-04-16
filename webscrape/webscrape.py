import requests
from bs4 import BeautifulSoup
import pandas as pd
import modules.query as q
from sqlalchemy import create_engine

    

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
        

        username = 'eric'
        password = 'nomeat555'
        host = '96.38.123.26'  # or your host, e.g., '127.0.0.1'
        database = 'basketballstats'

        # Create a MySQL engine
        engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}/{database}')

        df.to_sql('stats_23_24', con=engine, if_exists='replace', index=False)


def update_table():
    url = 'https://www.basketball-reference.com/leagues/NBA_2024_per_game.html'

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the table containing player statistics
        table = soup.find('table', {'id': 'per_game_stats'})

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
        # df = pd.DataFrame(player_data, columns=headers)
        conn = q.connect_to_database()
        cursor = conn.cursor()
        for row in player_data:
            RK = row[0]
            print(RK)
            sql_query = f""" UPDATE basketballstats.stats_23_24
                SET 
                    Player = '{row[1]}',
                    Pos = '{row[2]}',
                    Age = {row[3]},
                    Tm = '{row[4]}',
                    G = {row[5]},
                    GS = {row[6]},
                    MP = {row[7]},
                    FG = {row[8]},
                    FGA = {row[9]},
                    `FG%` = {row[10]},
                    3P = {row[11]},
                    3PA = {row[12]},
                    `3P%` = {row[13]},
                    2P = {row[14]},
                    2PA = {row[15]},
                    `2P%` = {row[16]},
                    `eFG%` = {row[17]},
                    FT = {row[18]},
                    FTA = {row[19]},
                    `FT%` = {row[20]},
                    ORB = {row[21]},
                    DRB = {row[22]},
                    TRB = {row[23]},
                    AST = {row[24]},
                    STL = {row[25]},
                    BLK = {row[26]},
                    TOV = {row[27]},
                    PF = {row[28]},
                    PTS = {row[29]}

                WHERE RK = {RK}"""
        
            cursor.execute(sql_query)


        # Commit changes
        conn.commit()

        # Close connection
        cursor.close()
        conn.close()


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
            # print(player_name)
            
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
    url = "https://www.basketball-reference.com/boxscores/?month=04&day=3&year=2024"
    response = requests.get(url)
    #print(response.status_code)
# Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')
        div_elements = soup.find_all('div', class_='game_summary expanded nohover')
        quarter = ""
        score = ""
        for div in div_elements:
            td_elements = div.find_all('td')
            for td in td_elements:
                
                if td.find_parents('table', class_='teams'):
                    continue

                if td.find('a', href=lambda href: href and '/teams/' in href and '/players/' not in href):

                    counter = 0
                    team = td.find('a')['href'].split('/')[2]
                    print("Team", team)
                    
                if 'center' in td.get('class', []):
                    score = td.get_text(strip=True)
                    if counter <= 4:
                        quarter = f"q{counter}_teamScoring"
                    elif counter == 5: 
                        quarter = "OT_teamScoring"
                    elif counter == 6:
                        quarter = "2OT_teamScoring"

                    print(quarter, score)
                    conn = q.connect_to_database()
                    sql_query = f"""UPDATE basketballstats.last_5_games
                                SET {quarter} = "{score}"
                                WHERE Date = "2024-04-03" 
                                AND Team = "{team}" AND {quarter} IS NULL"""
                
                    cursor = conn.cursor()
                    cursor.execute(sql_query)
                    conn.commit()
                    cursor.close()
                    conn.close()

                counter += 1
                # print(quarter, score)

                # conn = q.connect_to_database()
                # sql_query = f"""UPDATE basketballstats.last_5_games
                #                 SET {quarter} = "{score}"
                #                 WHERE Date = "2024-03-18" 
                #                 AND Team = "{team}" AND {quarter} IS NULL"""
                
                # cursor = conn.cursor()
                # cursor.execute(sql_query)
                # conn.commit()
                # cursor.close()
                # conn.close()
    else: 
        print("fail")

