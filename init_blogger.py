
import requests
from urllib.parse import urlparse, parse_qs

# This should match one of the Redirect URIs configured in your Google Cloud project
DEFAULT_REDIRECT_URI = "http://localhost"

def get_blogger_access_token():
    """
    Guides the user through the OAuth2 flow to get a Blogger access token.
    """
    print("--- Blogger OAuth2 Setup ---")
    
    # 1. Get Client ID and Secret from the user
    client_id = input("Enter your Google Cloud Client ID: ")
    client_secret = input("Enter your Google Cloud Client Secret: ")
    redirect_uri = input(f"Enter your Redirect URI (default: {DEFAULT_REDIRECT_URI}): ") or DEFAULT_REDIRECT_URI

    if not client_id or not client_secret:
        print("Client ID and Client Secret are required.")
        return

    # Scopes for Blogger API
    # https://developers.google.com/blogger/docs/v3/auth
    scope = "https://www.googleapis.com/auth/blogger"

    # 2. Construct the authorization URL
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope}&"
        f"response_type=code&"
        f"access_type=offline" # To get a refresh token
    )
    
    print("\nStep 1: Copy the following URL.")
    print("Step 2: Paste it into your browser's address bar and press Enter.")
    print("Step 3: Log in to your Google account and authorize this application.")
    print("Step 4: After authorizing, your browser will redirect to your Redirect URI (e.g., http://localhost). Copy the FULL URL from your browser's address bar on that final page and paste it below.")
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
    token_url = "https://accounts.google.com/o/oauth2/token"
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'code': auth_code,
        'grant_type': 'authorization_code'
    }
    
    try:
        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        token_data = response.json()
        
        access_token = token_data.get('access_token')
        refresh_token = token_data.get('refresh_token')
        
        if access_token:
            print("\n--- SUCCESS! ---")
            print("Your Blogger Access Token is:")
            print(f"\nAccess Token: {access_token}\n")
            if refresh_token:
                print(f"Refresh Token: {refresh_token}\n")
                print("Store the Refresh Token in config.py to automatically renew access tokens.")
            print("Please copy the Access Token and paste it into your config.py file for the 'access_token' field under 'blogger'.")
            print("Also, update 'client_id', 'client_secret', and 'redirect_uris' in config.py.")
            print("You will also need your Blogger Blog ID.")
        else:
            print(f"Could not retrieve access token. Response: {token_data}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while requesting the access token: {e}")
        if e.response:
            print(f"Response body: {e.response.text}")

if __name__ == '__main__':
    get_blogger_access_token()
