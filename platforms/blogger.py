import requests
import markdown
import json
from requests_oauthlib import OAuth2Session

# Path to the config file (assuming it's one level up from platforms/)
CONFIG_FILE_PATH = "/Users/bezal/blog_poster/config.py"

def _update_config_file(new_config, logger):
    """
    Updates the config.py file with new token information.
    This is a direct file manipulation and should be used carefully.
    """
    try:
        with open(CONFIG_FILE_PATH, 'r') as f:
            lines = f.readlines()

        # Find the PLATFORM_CONFIGS dictionary start and end
        start_line = -1
        end_line = -1
        for i, line in enumerate(lines):
            if "PLATFORM_CONFIGS = {" in line:
                start_line = i
            if start_line != -1 and line.strip() == ")":
                end_line = i
                break
        
        if start_line == -1 or end_line == -1:
            logger.error("Could not find PLATFORM_CONFIGS in config.py. Cannot update token.")
            return False

        # Extract the existing config string
        existing_config_str = "".join(lines[start_line : end_line + 1])
        # Safely evaluate the string to a Python dict
        existing_config = eval(existing_config_str)

        # Update the specific platform's config
        existing_config['blogger'] = new_config['blogger']

        # Convert back to string representation for writing
        # This is a simplified approach; a proper config parser/writer would be better
        updated_config_str = "PLATFORM_CONFIGS = " + json.dumps(existing_config, indent=4)

        # Replace the old config block with the new one
        new_lines = lines[:start_line] + [updated_config_str + "\n"] + lines[end_line + 1:]

        with open(CONFIG_FILE_PATH, 'w') as f:
            f.writelines(new_lines)
        logger.info("Config.py updated with new Blogger access token.")
        return True
    except Exception as e:
        logger.error(f"Failed to update config.py: {e}", exc_info=True)
        return False

def _refresh_blogger_token(config, logger):
    """
    Refreshes the Blogger access token using the refresh token.
    """
    client_id = config.get("client_id")
    client_secret = config.get("client_secret")
    refresh_token = config.get("refresh_token")
    redirect_uris = config.get("redirect_uris")

    if not all([client_id, client_secret, refresh_token, redirect_uris]):
        logger.error("Missing client_id, client_secret, refresh_token, or redirect_uris for Blogger token refresh.")
        return None

    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }

    try:
        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        token_data = response.json()

        new_access_token = token_data.get('access_token')
        if new_access_token:
            logger.info("Blogger access token refreshed successfully.")
            # Update the config dictionary in memory
            config['access_token'] = new_access_token
            # Persist the updated config to file
            _update_config_file(config, logger)
            return new_access_token
        else:
            logger.error(f"Failed to get new access token during refresh: {token_data}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Error during Blogger token refresh: {e}", exc_info=True)
        if e.response:
            logger.error(f"Refresh token response body: {e.response.text}")
        return None

def publish(post_metadata, post_content, config, logger, local_image_paths=None, author=None, date=None, description=None):
    """
    Publishes a post to Blogger.

    Args:
        post_metadata (dict): The metadata from the markdown file.
        post_content (str): The body content from the markdown file.
        config (dict): The platform-specific configuration.
        logger (logging.Logger): The logger instance.
        local_image_paths (list): List of absolute paths to local images found in markdown.
        author (str): Author name from front-matter.
        date (str): Date from front-matter.
        description (str): Description from front-matter.

    Returns:
        bool: True if successful, False otherwise.
    """
    logger.info("Attempting to publish to Blogger...")
    if local_image_paths:
        logger.warning("Blogger does not currently support direct image uploads via this script. Images will be skipped.")
    access_token = config.get("access_token")
    blog_id = config.get("blog_id")

    if not access_token or access_token == "YOUR_BLOGGER_ACCESS_TOKEN":
        logger.error("Error: Blogger Access Token is missing or not set in config.py.")
        return False
    if not blog_id or blog_id == "YOUR_BLOGGER_BLOG_ID":
        logger.error("Error: Blogger Blog ID is missing or not set in config.py.")
        return False

    api_url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Blogger expects content in HTML format.
    html_content = markdown.markdown(post_content)

    data = {
        "kind": "blogger#post",
        "blog": {
            "id": blog_id
        },
        "title": post_metadata.get("title", "No Title"),
        "content": html_content,
        "labels": post_metadata.get("tags", []) # Blogger uses labels for tags
    }

    # Add author if available
    if author:
        data["author"] = {"displayName": author}

    # Add published date if available
    if date:
        # Blogger API expects RFC3339 format (e.g., 2025-08-26T12:00:00Z)
        # Assuming date from front-matter is in a parseable format
        try:
            from datetime import datetime
            # Attempt to parse and format the date
            parsed_date = datetime.fromisoformat(str(date).replace('Z', '+00:00')) # Handle Z for UTC
            data["published"] = parsed_date.isoformat(timespec='seconds') + 'Z'
        except ValueError:
            logger.warning(f"Could not parse date '{date}' for Blogger. Using default.")

    # Blogger API expects labels as a list of strings
    if isinstance(data["labels"], str):
        data["labels"] = [label.strip() for label in data["labels"].split(',')]

    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()

        response_data = response.json()
        post_url = response_data.get("url")
        logger.info(f"Successfully published to Blogger! URL: {post_url}")
        return True

    except requests.exceptions.RequestException as e:
        if e.response is not None and e.response.status_code == 401:
            logger.warning("Blogger access token expired. Attempting to refresh...")
            new_access_token = _refresh_blogger_token(config, logger)
            if new_access_token:
                logger.info("Retrying Blogger post with new access token...")
                headers["Authorization"] = f"Bearer {new_access_token}"
                try:
                    retry_response = requests.post(api_url, headers=headers, json=data)
                    retry_response.raise_for_status()
                    retry_response_data = retry_response.json()
                    retry_post_url = retry_response_data.get("url")
                    logger.info(f"Successfully published to Blogger after refresh! URL: {retry_post_url}")
                    return True
                except requests.exceptions.RequestException as retry_e:
                    logger.error(f"Blogger post failed even after token refresh: {retry_e}", exc_info=True)
                    if retry_e.response:
                        logger.error(f"Retry response body: {retry_e.response.text}")
                    return False
            else:
                logger.error("Failed to refresh Blogger token. Cannot publish.")
                return False
        else:
            logger.error(f"Error publishing to Blogger: {e}", exc_info=True)
            if e.response:
                logger.error(f"Response body: {e.response.text}")
            return False
    blog_id = config.get("blog_id")

    if not access_token or access_token == "YOUR_BLOGGER_ACCESS_TOKEN":
        logger.error("Error: Blogger Access Token is missing or not set in config.py.")
        return False
    if not blog_id or blog_id == "YOUR_BLOGGER_BLOG_ID":
        logger.error("Error: Blogger Blog ID is missing or not set in config.py.")
        return False

    api_url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Blogger expects content in HTML format.
    html_content = markdown.markdown(post_content)

    data = {
        "kind": "blogger#post",
        "blog": {
            "id": blog_id
        },
        "title": post_metadata.get("title", "No Title"),
        "content": html_content,
        "labels": post_metadata.get("tags", []) # Blogger uses labels for tags
    }

    # Blogger API expects labels as a list of strings
    if isinstance(data["labels"], str):
        data["labels"] = [label.strip() for label in data["labels"].split(',')]

    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()

        response_data = response.json()
        post_url = response_data.get("url")
        logger.info(f"Successfully published to Blogger! URL: {post_url}")
        return True

    except requests.exceptions.RequestException as e:
        if e.response is not None and e.response.status_code == 401:
            logger.warning("Blogger access token expired. Attempting to refresh...")
            new_access_token = _refresh_blogger_token(config, logger)
            if new_access_token:
                # Retry the request with the new token
                logger.info("Retrying Blogger post with new access token...")
                headers["Authorization"] = f"Bearer {new_access_token}"
                try:
                    retry_response = requests.post(api_url, headers=headers, json=data)
                    retry_response.raise_for_status()
                    retry_response_data = retry_response.json()
                    retry_post_url = retry_response_data.get("url")
                    logger.info(f"Successfully published to Blogger after refresh! URL: {retry_post_url}")
                    return True
                except requests.exceptions.RequestException as retry_e:
                    logger.error(f"Blogger post failed even after token refresh: {retry_e}", exc_info=True)
                    if retry_e.response:
                        logger.error(f"Retry response body: {retry_e.response.text}")
                    return False
            else:
                logger.error("Failed to refresh Blogger token. Cannot publish.")
                return False
        else:
            logger.error(f"Error publishing to Blogger: {e}", exc_info=True)
            if e.response:
                logger.error(f"Response body: {e.response.text}")
            return False