import requests
import flask
from flask import session, redirect, request
import json
import spotipy
from PIL import Image
import urllib.request
from urllib.parse import quote
import os
from phue import Bridge
from rgbxy import Converter
from dotenv import load_dotenv
from util.LightController import LightController
from util.ImageProcessor import ImageProcessor

load_dotenv()

app = flask.Flask(__name__)
app.config["DEBUG"] = True

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_SECRET_ID = os.getenv('SPOTIFY_SECRET_ID')
SPOTIFY_REDIRECT_URI = 'http://127.0.0.1:5000/callback/q'
SPOTIFY_CURRENTLY_PLAYING_ENDPOINT = 'https://api.spotify.com/v1/me/player/currently-playing'

TEMP_ALBUM_FILE = 'albumArt.jpg'

authQueryParameters = {
    "response_type": "code",
    "redirect_uri": SPOTIFY_REDIRECT_URI,
    "scope": 'user-read-currently-playing',
    "client_id": SPOTIFY_CLIENT_ID,
}

@app.route('/')
def index():
    urlArgs = "&".join(["{}={}".format(key, quote(val)) for key, val in authQueryParameters.items()])
    authUrl = "{}/?{}".format(SPOTIFY_AUTH_URL, urlArgs)
    return redirect(authUrl)

#https://github.com/drshrey/spotify-flask-auth-example/blob/master/main.py
@app.route('/callback/q')
def callback():
    authToken = request.args['code']
    tokenPayload = {
        "grant_type": "authorization_code",
        "code": str(authToken),
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_SECRET_ID
    }

    tokenPost = requests.post(SPOTIFY_TOKEN_URL, data=tokenPayload)
    tokenResponse = json.loads(tokenPost.text)

    access_token = tokenResponse["access_token"]
    # refresh_token = tokenResponse["refresh_token"]
    # token_type = tokenResponse["token_type"]
    # expires_in = tokenResponse["expires_in"]

    session['token'] = access_token
    return redirect('http://127.0.0.1:5000/home')

    
@app.route('/home')    
def displayColors():
    access_token = session['token']
    authorizaton_header = {"Authorization": "Bearer {}".format(access_token)}

    currentlyPlayingResponse = requests.get(SPOTIFY_CURRENTLY_PLAYING_ENDPOINT, headers = authorizaton_header)
    currentlyPlaying = json.loads(currentlyPlayingResponse.text)

    imageProcessor = ImageProcessor()

    if currentlyPlaying is not None:
        trackName = currentlyPlaying['item']['name']
        artist = currentlyPlaying['item']['artists'][0]['name']
        image = currentlyPlaying['item']['album']['images'][0]['url']
        colors = imageProcessor.getTopThreeColors(image)
    else:
        trackName = 'nothing'
        artist = 'nobody'
        image = 'no pics'
        colors = 'no colors'

    colorBands = ''
    i = 0
    for color in colors:
        colorBands = colorBands + \
            f"<div><div>{i}: This color is {color[1]}</div><div style='background-color: rgb{color[1]};'><br><br></div></div>"
        i = i + 1

    color1 = colors[0][1]
    color2 = colors[1][1]
    color3 = colors[2][1]

#good examples
#hypa hypa, mothership, psycho, the stomach for it

    lightController = LightController(os.getenv('BRIDGE_IP_ADDRESS'))

    lightController.setLight('Kitchen1', color1[0], color1[1], color1[2])
    lightController.setLight('Kitchen2', color2[0], color2[1], color2[2])
    lightController.setLight('Kitchen3', color3[0], color3[1], color3[2])

    return (f"<h1>Currently Playing {trackName} by {artist}</h1>" + colorBands)

if __name__ == "__main__":                                                      
    app.secret_key = os.urandom(24)                                             
    app.run()