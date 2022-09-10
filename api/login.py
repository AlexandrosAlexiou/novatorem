import os
from dotenv import load_dotenv, find_dotenv
import urllib.parse

load_dotenv(find_dotenv())

REDIRECT_URI = os.getenv("REDIRECT_URI")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
STATE = os.getenv("STATE")


def getLoginUrl():
    scopes = ['user-read-currently-playing', 'user-read-recently-played']
    parameters = {'client_id': SPOTIFY_CLIENT_ID, 'redirect_uri': REDIRECT_URI,
                  'response_type': 'code', "scope": ','.join(scopes), 'show_dialog': 'false', "state": STATE}

    encoded_parameters = urllib.parse.urlencode(parameters)
    login_url = f'https://accounts.spotify.com/authorize?{encoded_parameters}'
    return login_url
