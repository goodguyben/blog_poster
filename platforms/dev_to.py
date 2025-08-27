"""
Handles publishing to Dev.to.
"""

import requests

def publish(post_metadata, post_content, config, logger, local_image_paths=None, author=None, date=None, description=None):
    """
    Publishes a post to Dev.to.

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
    logger.info("Attempting to publish to Dev.to...")
    if local_image_paths:
        logger.warning("Dev.to does not currently support direct image uploads via this script. Images will be skipped.")
    api_key = config.get("api_key")
    if not api_key or api_key == "YOUR_DEV_TO_API_KEY":
        logger.error("Error: Dev.to API key is missing or not set in config.py.")
        return False

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }

    # Dev.to API expects the tags as a list of strings
    tags = post_metadata.get('tags', [])
    if isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(',')]

    data = {
        "article": {
            "title": post_metadata.get("title", "No Title"),
            "body_markdown": post_content,
            "published": post_metadata.get("published", False),
            "tags": tags,
        }
    }

    # Add description if available
    if description:
        data["article"]["description"] = description

    try:
        response = requests.post("https://dev.to/api/articles", headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        response_data = response.json()
        logger.info(f"Successfully published to Dev.to! URL: {response_data.get('url')}")
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Error publishing to Dev.to: {e}")
        if e.response:
            logger.error(f"Response body: {e.response.text}")
        return False
