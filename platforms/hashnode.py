"""
Handles publishing to Hashnode.
"""

import requests

def publish(post_metadata, post_content, config, logger, local_image_paths=None, author=None, date=None, description=None):
    """
    Publishes a post to Hashnode.

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
    logger.info("Attempting to publish to Hashnode...")
    if local_image_paths:
        logger.warning("Hashnode does not currently support direct image uploads via this script. Images will be skipped.")
    api_key = config.get("api_key")
    publication_id = config.get("publication_id")

    if not api_key or api_key == "YOUR_HASHNODE_API_KEY":
        logger.error("Error: Hashnode API key is missing or not set in config.py.")
        return False
    if not publication_id or publication_id == "YOUR_HASHNODE_PUBLICATION_ID":
        logger.error("Error: Hashnode Publication ID is missing or not set in config.py.")
        return False

    headers = {
        "Content-Type": "application/json",
        "Authorization": api_key
    }

    # Hashnode expects tags to be a list of dictionaries with 'id' or 'name' and 'slug'
    # For simplicity, we'll pass them as names and let Hashnode handle creating them.
    # This requires a more complex query if we want to use existing tags by ID.
    tags = post_metadata.get('tags', [])
    if isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(',')]
    
    # The API expects a list of TagInput objects, which are dicts.
    tag_inputs = []
    for tag_name in tags:
        # A simple way to generate a slug, Hashnode might do this differently
        slug = tag_name.lower().replace(' ', '-')
        tag_inputs.append({"name": tag_name, "slug": slug})

    mutation = """
    mutation publishPost($input: PublishPostInput!) {
      publishPost(input: $input) {
        post {
          slug
          url
        }
      }
    }
    """

    variables = {
        "input": {
            "title": post_metadata.get("title", "No Title"),
            "contentMarkdown": post_content,
            "publicationId": publication_id,
            "tags": tag_inputs
        }
    }

    # Add description (subtitle) if available
    if description:
        variables["input"]["subtitle"] = description

    try:
        response = requests.post("https://gql.hashnode.com/", headers=headers, json={"query": mutation, "variables": variables})
        response.raise_for_status()

        response_data = response.json()
        if "errors" in response_data:
            logger.error(f"Error publishing to Hashnode: {response_data['errors']}")
            return False

        post_info = response_data.get('data', {}).get('publishPost', {}).get('post', {})
        if post_info:
            logger.info(f"Successfully published to Hashnode! URL: {post_info.get('url')}")
            return True
        else:
            logger.error(f"Failed to publish to Hashnode. Response: {response_data}")
            return False

    except requests.exceptions.RequestException as e:
        logger.error(f"Error publishing to Hashnode: {e}")
        if e.response:
            logger.error(f"Response body: {e.response.text}")
        return False

