from flask import Flask, redirect, request, jsonify
import requests
import base64
import random
import string
import tkinter_app

app = Flask(__name__)

client_id = '88ed3e4d54414402b2dc0040684a0867'
client_secret = 'bfefd0811b314faaa357c4be12e9b9b8'  # Replace with your client secret
redirect_uri = 'http://localhost:8888/callback'

def generate_random_string(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

@app.route('/')
def index():
    state = generate_random_string(16)
    scope = 'user-read-private user-read-email user-modify-playback-state streaming'

    auth_url = (
        'https://accounts.spotify.com/authorize?'
        f'response_type=code&client_id={client_id}&scope={scope}&redirect_uri={redirect_uri}&state={state}'
    )
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')

    auth_str = f'{client_id}:{client_secret}'
    b64_auth_str = base64.urlsafe_b64encode(auth_str.encode()).decode()

    token_url = 'https://accounts.spotify.com/api/token'
    payload = {
        'code': code,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    headers = {
        'Authorization': f'Basic {b64_auth_str}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(token_url, data=payload, headers=headers)
    response_data = response.json()

    access_token = response_data.get('access_token')
    if access_token:
        # Start the Tkinter application
        tkinter_app.startTkinter()
        return redirect(f'http://localhost:8888/player?access_token={access_token}')
    else:
        return jsonify(response_data), 400

@app.route('/player')
def player():
    access_token = request.args.get('access_token')
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Spotify Web Playback SDK Quick Start</title>
    </head>
    <body>
        <h1>Spotify Web Playback SDK Quick Start</h1>
        <button id="togglePlay">Toggle Play</button>

        <script src="https://sdk.scdn.co/spotify-player.js"></script>
        <script>
            // JavaScript code for Spotify playback control here
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(port=8888, debug=True)
