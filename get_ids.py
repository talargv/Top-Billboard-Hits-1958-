import numpy as np
import pandas as pd
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# get client credentials
with open('info.txt') as info:
    lines = info.read().splitlines()
    CLIENT_ID = lines[0][lines[0].index(":") + 1:]
    CLIENT_SECRET = lines[1][lines[1].index(":") + 1:]

data = pd.read_csv('hits_data.csv') 

manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth=manager.get_access_token(as_dict=False),
    auth_manager=manager,
    client_credentials_manager=manager)


def get_song_id(row_num, q_gen_func, df=data):
    song_name = df.at[row_num,'Single']
    sp_id = 'N'
    try:
        sp_id = df.at[row_num, 'Spotify id']
    except KeyError:
        pass
    if not sp_id == 'N':
        print(f'{row_num}: {song_name} has id {sp_id}')
        return 
    else:
        header = {"Authorization": "Bearer " + manager.get_access_token(as_dict=False)}
        req = requests.get(f"https://api.spotify.com/v1/search?q={q_gen_func(row_num)}&type=track&limit=1", headers=header)
        try:
            song_id = req.json()["tracks"]["items"][0]["id"]
            return (song_id, True)
        except (IndexError, KeyError):
            return (req.json(), False)


def degenerate_query(row_num):
    song_name = data.at[row_num,'Single']
    artist_name = data.at[row_num,'Artist(s)']
    return f'{song_name}+artist:{artist_name.split()[0]}'


def fill_in_value(row_num, q_gen_func, df=data):
    try_song_id = get_song_id(row_num, q_gen_func)
    if try_song_id[1] == False:
        print(f'Error getting data for row {row_num}. Recieved\n{try_song_id[0]}')
    else:
        df.at[row_num, 'Spotify id'] = try_song_id[0]
        print(df.at[row_num, 'Spotify id'])


updated = pd.read_csv('hits_data.csv')

def update_all():
    updated['Spotify id'] = 'N'
    miss = updated.loc[updated['Spotify id'] == 'N']
    up = miss['Unnamed: 0'].values.tolist()
    for i in up:
        fill_in_value(i, q_gen_func=degenerate_query, df=updated)

update_all()
updated.to_csv('hits_data_final.csv')