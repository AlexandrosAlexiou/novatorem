import os
import requests

from dotenv import load_dotenv, find_dotenv
from base64 import b64encode

from .constants import ACCESS_TOKEN_URL
from .exceptions import EmptyResponse


class SpotifyClient():

    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_token = None
        self.refresh_token = None
        self.SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
        self.SPOTIFY_SECRET = os.getenv("SPOTIFY_SECRET")
        self.REDIRECT_URI = os.getenv("REDIRECT_URI")
        self.authorization_code = b64encode(
            f"{self.SPOTIFY_CLIENT_ID}:{self.SPOTIFY_SECRET}".encode()).decode("ascii")

    def authenticate(self, code):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {self.authorization_code}',
        }
        data = f'grant_type=authorization_code&redirect_uri={self.REDIRECT_URI}&code={code}'

        response = requests.post(
            ACCESS_TOKEN_URL, headers=headers, data=data).json()
        self.access_token, self.refresh_token = response["access_token"], response["refresh_token"]

    def refreshAccessToken(self):
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        headers = {"Authorization": "Basic {}".format(self.authorization_code)}
        response = requests.post(
            ACCESS_TOKEN_URL, data=data, headers=headers).json()
        self.access_token = response["access_token"]

    def get(self, url):
        response = requests.get(
            url, headers={"Authorization": f"Bearer {self.access_token}"})

        if response.status_code == 401:
            self.refreshAccessToken()
            response = requests.get(
                url, headers={"Authorization": f"Bearer {self.access_token}"}).json()
            return response
        elif response.status_code == 204:
            raise EmptyResponse(f"{url} returned no data.")
        else:
            return response.json()

    def getAccessToken(self):
        return self.access_token

    def getRefreshToken(self):
        return self.refresh_token

    def getTokens(self):
        return self.access_token, self.refresh_token
