"""
Parses a Markdown file to extract front-matter and body content.
"""
import frontmatter
import re
import os

def parse_markdown(file_path):
    """
    Reads a Markdown file, separates its front-matter and content, and extracts local image paths.

    Args:
        file_path (str): The path to the markdown file.

    Returns:
        tuple: A tuple containing the post's metadata (dict), content (str), and a list of local image paths (list).
               Returns (None, None, None) if the file cannot be read or parsed.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
            metadata = post.metadata
            content = post.content

            local_image_paths = []
            # Regex to find Markdown image syntax: ![alt text](image_path)
            # Group 1: alt text, Group 2: image_path
            image_pattern = re.compile(r'!\[.*?\]\((.*?)\)')
            
            # Find all image paths
            found_image_paths = image_pattern.findall(content)

            # Determine if path is local or external URL
            for img_path in found_image_paths:
                if not img_path.startswith(('http://', 'https://')):
                    # Resolve relative paths to absolute paths based on the markdown file's directory
                    abs_img_path = os.path.abspath(os.path.join(os.path.dirname(file_path), img_path))
                    local_image_paths.append(abs_img_path)

            return metadata, content, local_image_paths
    except Exception as e:
        print(f"Error parsing markdown file: {e}")
        return None, None, None
