"""
Handles publishing to Tumblr.
"""

import pytumblr
import markdown

def publish(post_metadata, post_content, config, logger, local_image_paths=None, author=None, date=None, description=None):
    """
    Publishes a post to Tumblr.

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
    logger.info("Attempting to publish to Tumblr...")
    if local_image_paths:
        logger.warning("Tumblr does not currently support direct image uploads via this script. Images will be skipped.")
    consumer_key = config.get("client_id") # Tumblr uses client_id as consumer_key
    consumer_secret = config.get("client_secret") # Tumblr uses client_secret as consumer_secret
    oauth_token = config.get("access_token")
    oauth_token_secret = config.get("refresh_token") # Using refresh_token as oauth_token_secret
    blog_hostname = config.get("blog_hostname")

    if not all([consumer_key, consumer_secret, oauth_token, oauth_token_secret, blog_hostname]):
        logger.error("Error: Missing Tumblr credentials or blog_hostname in config.py.")
        return False

    # Initialize the Tumblr client
    client = pytumblr.TumblrRestClient(
        consumer_key,
        consumer_secret,
        oauth_token,
        oauth_token_secret
    )

    # Tumblr API expects content in HTML format for text posts
    html_content = markdown.markdown(post_content)

    # Prepare optional parameters
    optional_params = {}
    if date:
        # Tumblr API expects RFC 3339 format (e.g., 2025-08-26T12:00:00Z)
        # Assuming date from front-matter is in a parseable format
        try:
            from datetime import datetime
            parsed_date = datetime.fromisoformat(str(date).replace('Z', '+00:00'))
            optional_params['date'] = parsed_date.isoformat(timespec='seconds') + 'Z'
        except ValueError:
            logger.warning(f"Could not parse date '{date}' for Tumblr. Using default.")

    try:
        response = client.create_text(
            blog_hostname,
            title=post_metadata.get("title", "No Title"),
            body=html_content,
            **optional_params
        )

        if response and response.get('id'):
            # Tumblr API doesn't return a direct URL in the create response for text posts
            # The URL is usually derived from blog_hostname and post_id
            post_id = response.get('id')
            post_url = f"https://{blog_hostname}/post/{post_id}"
            logger.info(f"Successfully published to Tumblr! Post ID: {post_id}, URL: {post_url}")
            return True
        else:
            logger.error(f"Failed to publish to Tumblr. Response: {response}")
            return False

    except Exception as e:
        logger.error(f"An error occurred while publishing to Tumblr: {e}")
        return False
