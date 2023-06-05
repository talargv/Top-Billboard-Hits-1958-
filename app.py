# works.csv is the right one
# create the fucking playlist already
# dont forget using venv on the folder

import json as js
import time


from flask import Flask, request, url_for, session, redirect
import pandas as pd
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth


class TokenError(Exception):
    pass

DATA = pd.read_csv('hits_data_final.csv')['Spotify id'].tolist()
DATA_URIS = [f'spotify:track:{song_id}' for song_id in DATA if song_id != 'N']
MAX_REQ_SIZE = 100
DATA_CHUNKS = [DATA_URIS[i:i+MAX_REQ_SIZE] for i in range(0, len(DATA_URIS), MAX_REQ_SIZE)]

with open('info.txt') as info:
    lines = info.read().splitlines()
    CLIENT_ID = lines[0][lines[0].index(":") + 1:]
    CLIENT_SECRET = lines[1][lines[1].index(":") + 1:]

app = Flask(__name__)

app.secret_key = 'OIauhaNK7105'
app.config['SESSION_COOKIE_NAME'] = 'My Cookie'
TOKEN_INFO = 'token_info'

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    sp_oauth = create_spotify_oauth()
    #print(request.args)
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('playlist_created', _external=True))

@app.route('/success')
def playlist_created():
    try:
        token_info = get_token()
    except TokenError:
        print("user not logged in")
        return redirect(url_for("login", _external=False))

    sp = spotipy.Spotify(auth=token_info['access_token'])
    user_id = sp.current_user()['id']
    playlist_id = sp.user_playlist_create(user=user_id, name="Top 10 Billboard 1958-", description='Created using Python')['id']
    for chunk in DATA_CHUNKS:
        token_info = get_token()
        #sp = spotipy.Spotify(auth=token_info['access_token'])
        append_playlist_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        append_playlist_headers = {'Authorization' : 'Bearer ' + token_info['access_token'], 'Content-Type' : 'application/json'}
        #append_playlist_data = js.dumps({'uris' : chunk})
        append_playlist_data = {"uris" : chunk}
        append_playlist = requests.request(method='POST',
        url=append_playlist_url,
        json=append_playlist_data,
        headers=append_playlist_headers)
        print(append_playlist.json())
    return 'works'


def get_token():
    #print(session)
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise TokenError
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info
    


def create_spotify_oauth(req_scope=['playlist-modify-public','playlist-modify-private']):
    return SpotifyOAuth(
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        redirect_uri=url_for('redirect_page', _external=True),
        scope=req_scope)
