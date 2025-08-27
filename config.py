"""
Configuration for the blog poster.

IMPORTANT: Add this file to .gitignore and do not commit API keys.
"""

# A dictionary to hold API keys and other platform-specific settings.
# The script will read from this configuration.
PLATFORM_CONFIGS = {
    "dev_to": {
        "api_key": "iWuNXFwXWhHfRnGdCrdS9dYZ"
    },
    "hashnode": {
        "api_key": "b1a5e79e-dad0-4cba-81db-e8eee144ba2c",
        "publication_id": "68adce38027b70eb9ac8f1c4"
    },
    "wordpress": {
        "client_id": "123546",
        "client_secret": "xoIWPrQwr211KBOyj0BEP7dZU76YlRFety7nAPh5Z0poWZAdaMZIKhfIkJdtmxkC",
        "site_id": "247785910",
        "username": "bezaljohnbenny",
        "application_password": "$PvWW5%Uj4tR1erx7LVqMkV3",
        "access_token": "JetQ(fDZUWNU6eWVohi&a$TG3Oew)R5%cGSIh55O0GuTj!zp%w)5)m^9xqhh&$e$"
    },
    "write_as": {},
    "telegraph": {
        "access_token": "57175b0150daee3d383f69cda19591ef47381412d4298fbfc33e40545268"
    },
    "blogger": {
        "client_id": "446184285962-5kafkvqsigfg7e9nikco367rhpbrp6i1.apps.googleusercontent.com",
        "client_secret": "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",
        "redirect_uris": ["http://localhost"], # Or your registered redirect URI
        "access_token": "ya29.A0AS3H6Nw28_ABOaNFZ3azlpLWbgFRgBsotD-fseRjMqpozM4ftGW9jhVvGMAJuZq90CYutcgoMJXRsF3NPB3_LUzLlLCvA-vFEoGn0h2TT27u_sSvcqI2NomfoQYrsFtkMVLhgPfUJ9FSID_hihxz5x0cig2Yc7_u7JP-6vAEWXlyXg_zcXLb1t1E0Oeo-m22fV-bUqoaCgYKASQSARQSFQHGX2MidyeR0KtuH2xs5G9xyR3-EQ0206",
        "refresh_token": "1//066Iyv7Rb1kt1CgYIARAAGAYSNwF-L9Ir9m0EhwbBDBV6lUlP8rtR2bhlgn6hxCHks1MPAsu2VmwlFN7j15GFp53DDsGuK3-UlXs",
        "blog_id": "6479032551921044496" # The ID of the blog to post to
    },
    "tumblr": {
        "client_id": "slwd9vbYsuo9fG1XSlOkFZiOqQ8rfPuDmBPP60SM1SznOJ5fhY",
        "client_secret": "vOGcKi6A33VVjIi9jctND1bZanfjgh6LjSeYpuE61Ebq3ctjoM",
        "redirect_uris": ["http://localhost"], # Or your registered redirect URI
        "access_token": "ukmlhIxDYsa7SYQ1XwpR3dIz9AXezeDagxMBXon3E73NqcK3mP",
        "refresh_token": "8fPUWTCNFxQ3HDnYLWc6wr8fyW3QU7K5uuudGVW6ArnuxjeR4U",
        "blog_hostname": "beyondtheedge-blog" # e.g., yourblog.tumblr.com
    }
}
