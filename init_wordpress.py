
import requests
from urllib.parse import urlparse, parse_qs

# Using a standard localhost redirect URI for local/CLI applications.
REDIRECT_URI = "http://localhost"

def get_access_token():
    """
    Guides the user through the OAuth2 flow to get a WordPress.com access token.
    """
    print("--- WordPress.com OAuth2 Setup (Final Attempt) ---")
    
    # 1. Get Client ID and Secret from the user
    client_id = input("Enter your WordPress.com Client ID: ")
    client_secret = input("Enter your WordPress.com Client Secret: ")

    if not client_id or not client_secret:
        print("Client ID and Client Secret are required.")
        return

    # 2. Construct the authorization URL
    auth_url = f"https://public-api.wordpress.com/oauth2/authorize?client_id={client_id}&redirect_uri={REDIRECT_URI}&response_type=code"
    
    print("\nStep 1: Copy the following URL.")
    print("Step 2: Paste it into your browser's address bar and press Enter.")
    print("Step 3: Log in to WordPress.com and authorize this application.")
    print("Step 4: After authorizing, your browser will show an error or a blank page at a URL that starts with 'http://localhost'. This is expected.")
    print("Step 5: Copy the FULL URL from your browser's address bar on that final page and paste it below.")
    print("\n--- AUTHORIZATION URL ---")
    print(auth_url)
    print("-------------------------")
    
    redirected_url = input("\nEnter the full redirected URL here: ")

    # 3. Extract the authorization code from the redirected URL
    try:
        parsed_url = urlparse(redirected_url)
        query_params = parse_qs(parsed_url.query)
        auth_code = query_params.get('code', [None])[0]
        if not auth_code:
            print("Could not find 'code' in the redirected URL. Please try again.")
            return
    except Exception as e:
        print(f"An error occurred while parsing the URL: {e}")
        return

    print("\nAuthorization code extracted successfully. Exchanging it for an access token...")

    # 4. Exchange the authorization code for an access token
    token_url = "https://public-api.wordpress.com/oauth2/token"
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': REDIRECT_URI,
        'code': auth_code,
        'grant_type': 'authorization_code'
    }
    
    try:
        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        token_data = response.json()
        
        access_token = token_data.get('access_token')
        
        if access_token:
            print("\n--- SUCCESS! ---")
            print("Your WordPress.com Access Token is:")
            print(f"\n{access_token}\n")
            print("Please copy this token and paste it into your config.py file for the 'access_token' field under 'wordpress'.")
        else:
            print(f"Could not retrieve access token. Response: {token_data}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while requesting the access token: {e}")
        if e.response:
            print(f"Response body: {e.response.text}")

if __name__ == '__main__':
    get_access_token()
