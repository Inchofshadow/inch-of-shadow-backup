"""
Temporary SoundCloud OAuth callback server.
Run this, then open the auth URL in your browser.
After authorizing, it captures the code and exchanges it for a user token.
Delete this file after use.
"""
import http.server
import urllib.parse
import requests
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('SOUNDCLOUD_CLIENT_ID')
CLIENT_SECRET = os.getenv('SOUNDCLOUD_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:8080/callback'
TOKEN_FILE = '.sc_user_token.json'


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/callback':
            params = urllib.parse.parse_qs(parsed.query)
            code = params.get('code', [None])[0]

            if code:
                # Exchange code for token
                r = requests.post('https://api.soundcloud.com/oauth2/token', data={
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': REDIRECT_URI
                })

                if r.status_code == 200:
                    token_data = r.json()
                    token_data['obtained_at'] = time.time()
                    with open(TOKEN_FILE, 'w') as f:
                        json.dump(token_data, f, indent=2)

                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'<h1>Authorized! You can close this tab.</h1>')
                    print(f"\nToken saved to {TOKEN_FILE}")
                    print("You can close this server (Ctrl+C).")
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(f'<h1>Error: {r.text}</h1>'.encode())
                    print(f"\nToken exchange failed: {r.status_code} {r.text}")
            else:
                error = params.get('error', ['unknown'])[0]
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f'<h1>Error: {error}</h1>'.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress default logging


if __name__ == '__main__':
    print("Starting callback server on http://localhost:8080 ...")
    print(f"\nOpen this URL in your browser:\n")
    print(f"https://soundcloud.com/connect?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope=non-expiring%20*")
    print("\nWaiting for authorization...")

    server = http.server.HTTPServer(('localhost', 8080), CallbackHandler)
    try:
        server.handle_request()  # Handle just one request then stop
    except KeyboardInterrupt:
        pass
    server.server_close()
