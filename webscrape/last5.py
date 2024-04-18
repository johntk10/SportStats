import requests
from bs4 import BeautifulSoup
import pandas as pd
import modules.query as q
from sqlalchemy import create_engine
import time
from datetime import datetime, timedelta
import mysql.connector


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


def update_yesterday_game():
    url = "https://www.basketball-reference.com/boxscores/"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        div_elements = soup.find_all('table', class_='teams')
        # print(div_elements)
        for div in div_elements:
            a_tags = div.find_all('a', href=True)
            for index, tag in enumerate(a_tags):
                href = tag['href']
                if index == 0:  # First <a> tag
                    team1_name = href.split('/')[2]  # Extract the value after "teams/"
                    print("Value after 'teams/' in first href:", team1_name)
                elif index == 1:  # Second <a> tag
                    page_link = href
                    print("Whole link for second href:", page_link)
                elif index == 2:  # Third <a> tag
                    team2_name = href.split('/')[2]  # Extract the value after "teams/"
                    print("Value after 'teams/' in third href:", team2_name)
            time.sleep(3)
            url = "https://www.basketball-reference.com" + page_link
            # print(url)
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                team1_table_id = "box-{}-game-basic".format(team1_name)
                team2_table_id = "box-{}-game-basic".format(team2_name)

                team1_table = soup.find('table', id= team1_table_id)
                team2_table = soup.find('table', id=team2_table_id)
                # header1 = [th.text.strip() for th in team1_table.find('thead').find_all('th')]
                # header2 = [th.text.strip() for th in team2_table.find('thead').find_all('th')]

                player_data_team1 = []
                player_data_team2 = []
                today_date = (datetime.today() -  timedelta(days=1)).strftime('%Y-%m-%d')
                team1_score = team1_table.find('tfoot').find(['th', 'td'], attrs={'data-stat': 'pts'}).get_text(strip=True)
                team2_score = team2_table.find('tfoot').find(['th', 'td'], attrs={'data-stat': 'pts'}).get_text(strip=True)
                if team1_score > team2_score:
                    team1_score_string = 'W ' + team1_score + '-' + team2_score
                    team2_score_string = 'L ' + team2_score + '-' + team1_score
                else:
                    team1_score_string = 'L ' + team1_score + '-' + team2_score
                    team2_score_string = 'W ' + team2_score + '-' + team1_score

                other_data_team1 = [today_date, team1_name, '@', team2_name, team1_score_string, '*']
                other_data_team2 = [today_date, team2_name, '', team1_name, team2_score_string, '*']
               
                for row in team1_table.find('tbody').find_all('tr'):
                    player_row = [td.text.strip() for td in row.find_all(['th', 'td'])]
                    if "Did Not Play" in player_row or "Did Not Dress" in player_row or player_row[0] == 'Reserves':
                        continue
                    updated_row = player_row[:1] + other_data_team1 + player_row[1:] + [None] * 6
                    player_data_team1.append(updated_row)
                for row in team2_table.find('tbody').find_all('tr'):
                    player_row = [td.text.strip() for td in row.find_all(['th', 'td'])]
                    if "Did Not Play" in player_row or "Did Not Dress" in player_row or player_row[0] == 'Reserves':
                        continue

                    updated_row = player_row[:1] + other_data_team2 + player_row[1:] + [None] * 6
                    player_data_team2.append(updated_row)

                total_data = player_data_team1 + player_data_team2
                headers = ['Player', 'Date', 'Team', '`@`', 'Opp', 'Result', 'GS', 'MP', 'FG', 'FGA', '`FG%`', 
                           '3P', '3PA', '`3P%`', 'FT', 'FTA', '`FT%`', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 
                           'BLK', 'TOV', 'PF', 'PTS', '`+/-`', 'q1_teamScoring', 'q2_teamScoring', 'q3_teamScoring',
                            'q4_teamScoring', 'OT_teamScoring', '2OT_teamScoring']
                print(total_data)
                conn = q.connect_to_database()
                cursor = conn.cursor()
                sql_query = f""" INSERT INTO basketballstats.last_5_games
                                ({', '.join(headers)}) VALUES
                                ({', '.join(['%s'] * len(headers))}) """
                for row in total_data:
                    cursor.execute(sql_query, row)
                    
                
                conn.commit()
                cursor.close()
                conn.close()


def remove_the_oldest_game():
    conn = q.connect_to_database()
    sql_query = f"""DELETE t1
                    FROM basketballstats.last_5_games t1
                    JOIN (
                        SELECT Player, MIN(STR_TO_DATE(Date, '%Y-%m-%d')) AS min_date
                        FROM basketballstats.last_5_games
                        GROUP BY Player
                        HAVING COUNT(*) >= 6
                    ) t2 ON t1.Player = t2.Player AND STR_TO_DATE(t1.Date, '%Y-%m-%d') = t2.min_date"""
    
    cursor = conn.cursor()
    cursor.execute(sql_query)
    conn.commit()
    cursor.close()
    conn.close()
                                    

# update_yesterday_game()
# remove_the_oldest_game()


# # Initialize an empty list to store all players' data
# all_players_data = []

# # Column headers, adjust according to the actual table you're scraping
# headers = ['Player', 'Date', 'Team', '@', 'Opp', 'Result', 'GS', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'GmSc', '+/-']
# print(len(headers))

# player_ids = []
# with open('active_player_ids.txt', 'r') as file:  # Ensure the file is named 'player_ids.txt' and located in the correct directory
#     player_ids = [line.strip() for line in file.readlines()]

# #print(player_ids)

# for player_id in player_ids:
#     player_games = get_last_5_games(player_id)
#     #print(player_games)
#     for game in player_games:
#         all_players_data.append([player_id] + game)  # Add player ID to each game data
#         print(all_players_data)
# print(all_players_data)

# # Convert the list of player data into a DataFrame
# df = pd.DataFrame(all_players_data, columns=headers)

# # Database connection parameters

# username = 'eric'
# password = 'nomeat555'
# host = '96.38.123.26'  # or your host, e.g., '127.0.0.1'
# database = 'basketballstats'

# # Create a MySQL engine
# engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}/{database}')


# # Save the DataFrame to SQL
# df.to_sql('new_last_5_games', con=engine, if_exists='replace', index=False)
