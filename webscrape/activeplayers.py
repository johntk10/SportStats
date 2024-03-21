import requests
from bs4 import BeautifulSoup
import pandas as pd

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

player_ids = scrape_active_player_ids()
print("HERE")
print(player_ids)

with open('active_player_ids.txt', 'w') as file:
    for player_id in player_ids:
        file.write(player_id + '\n')