from flask import Flask, redirect, request, jsonify
import requests
import base64
import random
import string
import threading
import os
import webbrowser
import tkinter_app

app = Flask(__name__)

client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')

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
            window.onSpotifyWebPlaybackSDKReady = () => {{
                const token = '{access_token}';  // Use the access token from the query parameter
                const player = new Spotify.Player({{
                    name: 'Web Playback SDK Quick Start Player',
                    getOAuthToken: cb => {{ cb(token); }},
                    volume: 0.1
                }});

                player.addListener('ready', (event) => {{
                    const device_id = event.device_id;
                    console.log('Ready with Device ID', device_id);
                    transferPlayback(token, device_id);
                }});

                player.addListener('not_ready', (device_id) => {{
                    console.log('Device ID has gone offline', device_id);
                }});

                player.addListener('initialization_error', (message) => {{
                    console.error('Initialization Error:', message);
                }});

                player.addListener('authentication_error', (message) => {{
                    console.error('Authentication Error:', message);
                }});

                player.addListener('account_error', (message) => {{
                    console.error('Account Error:', message);
                }});

                document.getElementById('togglePlay').onclick = function() {{
                    player.togglePlay();
                }};

                player.connect().then(success => {{
                    if (success) {{
                        console.log('The Web Playback SDK successfully connected to Spotify!');
                    }}
                }});

                function transferPlayback(token, device_id) {{
                    fetch('https://api.spotify.com/v1/me/player', {{
                        method: 'PUT',
                        headers: {{
                            'Authorization': 'Bearer ' + token,
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{
                            device_ids: [device_id],
                            play: true,
                        }}),
                    }})
                    .then(response => {{
                        if (response.ok) {{
                            console.log('Playback transferred successfully');
                        }} else {{
                            console.error('Failed to transfer playback');
                        }}
                    }})
                    .catch(error => {{
                        console.error('Error transferring playback:', error);
                    }});
                }}
            }};
        </script>
    </body>
    </html>
    '''

def start_flask_app():
    app.run(port=8888, debug=True, use_reloader=False)

if __name__ == '__main__':
    # Start the Flask app in a new thread
    flask_thread = threading.Thread(target=start_flask_app)
    flask_thread.daemon = True  # Allow thread to be killed when main program exits
    flask_thread.start()

    # Start the Tkinter app in the main thread
    tkinter_app.startTkinter()
