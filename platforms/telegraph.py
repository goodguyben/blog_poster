"""
Handles publishing to Telegra.ph.
"""

import requests
import markdown

def publish(post_metadata, post_content, config, logger, local_image_paths=None, author=None, date=None, description=None):
    """
    Publishes a post to Telegra.ph.

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
    logger.info("Attempting to publish to Telegra.ph...")
    if local_image_paths:
        logger.warning("Telegra.ph does not currently support direct image uploads via this script. Images will be skipped.")
    access_token = config.get("access_token")

    if not access_token or access_token == "YOUR_TELEGRAPH_ACCESS_TOKEN":
        logger.error("Error: Telegra.ph Access Token is missing or not set in config.py.")
        return False

    api_url = "https://api.telegra.ph/createPage"

    # Telegra.ph content is an array of Node objects. For simplicity, we'll convert markdown to HTML
    # and wrap it in a single paragraph node.
    html_content = markdown.markdown(post_content)
    # Basic conversion to Telegra.ph Node format
    # For more complex markdown, a dedicated parser would be needed.
    content_nodes = [{'tag': 'p', 'children': [post_content]}]

    data = {
        'access_token': access_token,
        'title': post_metadata.get("title", "No Title"),
        'author_name': author if author else "", # Use author from front-matter
        'content': content_nodes # This needs to be a JSON string for the API
    }

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()

        response_data = response.json()
        if response_data.get('ok') and response_data.get('result'):
            page_url = response_data['result'].get('url')
            logger.info(f"Successfully published to Telegra.ph! URL: {page_url}")
            return True
        else:
            logger.error(f"Failed to publish to Telegra.ph. Response: {response_data}")
            return False

    except requests.exceptions.RequestException as e:
        logger.error(f"Error publishing to Telegra.ph: {e}")
        if e.response:
            logger.error(f"Response body: {e.response.text}")
        return False
