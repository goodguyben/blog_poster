"""
Main script to orchestrate the blog posting process.
"""
import os
import sys
import logging
import importlib
from blog_poster.parser import parse_markdown
from blog_poster.config import PLATFORM_CONFIGS

def setup_logger():
    """Sets up a logger to output to both console and a file."""
    logger = logging.getLogger("BlogPoster")
    logger.setLevel(logging.DEBUG)

    # Prevent adding duplicate handlers if this function is called again
    if logger.hasHandlers():
        return logger

    # File handler
    log_path = os.path.join(os.path.dirname(__file__), 'publishing.log')
    file_handler = logging.FileHandler(log_path)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger

# Dynamically import all publisher modules from the 'platforms' directory
PLATFORM_MODULES = {}
platforms_dir = os.path.join(os.path.dirname(__file__), 'platforms')
for filename in os.listdir(platforms_dir):
    if filename.endswith('.py') and not filename.startswith('__'):
        module_name = filename[:-3]
        try:
            module = importlib.import_module(f"blog_poster.platforms.{module_name}")
            if module_name in sys.modules:
                module = importlib.reload(module)
            PLATFORM_MODULES[module_name] = module
        except ImportError as e:
            # We need a logger here, but setup_logger hasn't been called yet.
            # A simple print is acceptable for this initial setup error.
            print(f"Could not import platform {module_name}: {e}")

def log_metadata(logger, metadata):
    """Logs the metadata of the parsed markdown file."""
    logger.info("Parsed Markdown successfully.")
    logger.info(f"Title: {metadata.get('title', 'N/A')}")
    logger.info(f"Tags: {metadata.get('tags', 'N/A')}")
    if metadata.get('author'):
        logger.info(f"Author: {metadata.get('author')}")
    if metadata.get('date'):
        logger.info(f"Date: {metadata.get('date')}")
    if metadata.get('description'):
        logger.info(f"Description: {metadata.get('description')}")


def publish_to_platforms(logger, metadata, content, local_image_paths):
    """Iterates through configured platforms and publishes the content."""
    for platform_name, module in sorted(PLATFORM_MODULES.items()):
        logger.info(f"\n--- Publishing to {platform_name.replace('_', '.').capitalize()} ---")
        if platform_name in PLATFORM_CONFIGS:
            config = PLATFORM_CONFIGS[platform_name]
            if hasattr(module, 'publish'):
                try:
                    success = module.publish(
                        metadata,
                        content,
                        config,
                        logger,
                        local_image_paths,
                        metadata.get('author'),
                        metadata.get('date'),
                        metadata.get('description')
                    )
                    if success:
                        logger.info(f"Successfully published to {platform_name}")
                    else:
                        logger.warning(f"Failed to publish to {platform_name}")
                except Exception as e:
                    logger.error(f"An unexpected error occurred while publishing to {platform_name}: {e}", exc_info=True)
            else:
                logger.warning(f"Platform module {platform_name} does not have a 'publish' function.")
        else:
            logger.warning(f"No configuration found for {platform_name}. Skipping.")

def main(markdown_file_path, logger):
    """
    Main function to read a markdown file and publish it to configured platforms.

    Args:
        markdown_file_path (str): The absolute path to the markdown file.
        logger (logging.Logger): The logger instance for logging output.
    """
    logger.info(f"--- Starting new blog distribution run for: {markdown_file_path} ---")

    try:
        metadata, content, local_image_paths = parse_markdown(markdown_file_path)
    except (ValueError, TypeError) as e:
        logger.error(f"Could not parse markdown file: {e}")
        return

    log_metadata(logger, metadata)
    publish_to_platforms(logger, metadata, content, local_image_paths)

    logger.info("--- Blog distribution run finished ---")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 -m blog_poster.main <path_to_markdown_file>")
        sys.exit(1)
    
    markdown_path = sys.argv[1]
    if not os.path.isabs(markdown_path):
        markdown_path = os.path.abspath(markdown_path)

    # Setup logger and run main function
    app_logger = setup_logger()
    main(markdown_path, app_logger)