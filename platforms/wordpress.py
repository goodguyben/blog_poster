import requests
import markdown
import os
import base64

# Path to the config file (assuming it's one level up from platforms/)
CONFIG_FILE_PATH = "/Users/bezal/blog_poster/config.py"

def _upload_image_to_wordpress(image_path, config, logger):
    """
    Uploads an image to WordPress.com's media library.
    """
    username = config.get("username")
    application_password = config.get("application_password")
    site_id = config.get("site_id")

    if not all([username, application_password, site_id]):
        logger.error("Missing WordPress.com username, application_password, or site ID for image upload.")
        return None

    media_api_url = f"https://public-api.wordpress.com/rest/v1.1/sites/{site_id}/media/new"

    # Basic Authentication
    credentials = f"{username}:{application_password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode('utf-8')

    headers = {
        "Authorization": f"Basic {encoded_credentials}"
    }

    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
            file_name = os.path.basename(image_path)
            
            # Use files parameter for multipart/form-data upload
            # WordPress.com API expects the filename in the files tuple
            files = {'media[]': (file_name, image_data, 'image/png')} # Assuming PNG for test_image.png
            
            logger.debug(f"Attempting image upload to {media_api_url} for {file_name}")
            response = requests.post(media_api_url, headers=headers, files=files)
            response.raise_for_status()

            response_data = response.json()
            if response_data and response_data.get('media') and len(response_data['media']) > 0:
                image_url = response_data['media'][0].get('url')
                logger.info(f"Successfully uploaded image {file_name} to WordPress.com. URL: {image_url}")
                return image_url
            else:
                logger.error(f"Failed to get image URL from WordPress.com upload response: {response_data}")
                return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Error uploading image to WordPress.com: {e}", exc_info=True)
        if e.response:
            logger.error(f"Image upload response body: {e.response.text}")
        return None

def publish(post_metadata, post_content, config, logger, local_image_paths=None, author=None, date=None, description=None):
    """
    Publishes a post to WordPress.com.

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
    logger.info("Attempting to publish to WordPress.com...")
    access_token = config.get("access_token")
    site_id = config.get("site_id")

    if not access_token or access_token == "YOUR_WORDPRESS_ACCESS_TOKEN":
        logger.error("Error: WordPress.com Access Token is missing or not set in config.py.")
        return False
    if not site_id or site_id == "YOUR_WORDPRESS_SITE_ID":
        logger.error("Error: WordPress.com Site ID is missing or not set in config.py.")
        return False

    # --- Image Handling ---
    updated_post_content = post_content
    if local_image_paths:
        logger.warning("WordPress.com image upload via API is not supported on your current plan. Images will be skipped. Please use externally hosted images.")
    # --- End Image Handling ---

    api_url = f"https://public-api.wordpress.com/rest/v1.1/sites/{site_id}/posts/new"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # WordPress API expects content in HTML format.
    html_content = markdown.markdown(updated_post_content)

    # Get tags and categories from metadata
    tags = post_metadata.get('tags', [])
    if isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(',')]
    
    categories = post_metadata.get('categories', [])
    if isinstance(categories, str):
        categories = [cat.strip() for cat in categories.split(',')]

    data = {
        "title": post_metadata.get("title", "No Title"),
        "content": html_content,
        "status": "publish" if post_metadata.get("published", False) else "draft",
        "tags": ",".join(tags), # API expects a comma-separated string for tags
        "categories": ",".join(categories)
    }

    # Add date if available
    if date:
        # WordPress API expects RFC3339 format (e.g., 2025-08-26T12:00:00Z)
        # Assuming date from front-matter is in a parseable format
        try:
            from datetime import datetime
            parsed_date = datetime.fromisoformat(str(date).replace('Z', '+00:00')) # Handle Z for UTC
            data["date"] = parsed_date.isoformat(timespec='seconds') + 'Z'
        except ValueError:
            logger.warning(f"Could not parse date '{date}' for WordPress.com. Using default.")

    # Add description as excerpt if available
    if description:
        data["excerpt"] = description

    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()

        response_data = response.json()
        post_url = response_data.get("URL", "")
        logger.info(f"Successfully published to WordPress.com! URL: {post_url}")
        return True

    except requests.exceptions.RequestException as e:
        if e.response is not None and e.response.status_code == 401:
            logger.warning("WordPress.com access token expired. Attempting to refresh...")
            # WordPress.com OAuth2 does not typically provide a refresh token for desktop apps
            # The access token is usually long-lived or requires re-authorization.
            # For simplicity, we'll just log the failure and ask the user to re-authorize.
            logger.error("WordPress.com token refresh not implemented for this OAuth flow. Please re-run init_wordpress.py to get a new token.")
            return False
        else:
            logger.error(f"Error publishing to WordPress.com: {e}", exc_info=True)
            if e.response:
                logger.error(f"Response body: {e.response.text}")
            return False