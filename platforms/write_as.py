"""
Handles publishing to Write.as.
"""

import requests

def publish(post_metadata, post_content, config, logger, local_image_paths=None, author=None, date=None, description=None):
    """
    Publishes a post to Write.as.

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
    logger.info("Attempting to publish to Write.as...")
    if local_image_paths:
        logger.warning("Write.as does not currently support direct image uploads via this script. Images will be skipped.")

    api_url = "https://write.as/api/posts"

    # Write.as API expects 'body' for content and 'title' for title
    data = {
        "title": post_metadata.get("title", ""),
        "body": post_content
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        response_data = response.json()
        logger.debug(f"Write.as raw response: {response_data}")
        post_url = response_data['data']["url"]
        logger.debug(f"Write.as initial post_url: {post_url}")
        if post_url:
            logger.debug("Write.as: post_url is truthy.")
            # Write.as returns a .md URL, the viewable URL is without .md
            if post_url.endswith('.md'):
                post_url = post_url[:-3]
                logger.debug(f"Write.as post_url after stripping .md: {post_url}")
            logger.info(f"Successfully published to Write.as! URL: {post_url}")
            return True
        else:
            logger.debug("Write.as: post_url is falsy.")
            logger.error(f"Failed to publish to Write.as. No URL in response: {response_data}")
            return False

    except requests.exceptions.RequestException as e:
        logger.error(f"Error publishing to Write.as: {e}")
        if e.response:
            logger.error(f"Response body: {e.response.text}")
        return False
