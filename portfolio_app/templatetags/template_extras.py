# LehmanCustomConstruction/templatetags/template_extras.py
from django import template
import logging  # Import the logging library

# Get a logger instance specific to this module
logger = logging.getLogger(__name__)

# Standard registration line
register = template.Library()

# Log a message when Django tries to load this file
logger.info("########## Trying to load template_extras.py ##########")

@register.filter(name='test_filter')
def test_filter(value):
    logger.info("########## test_filter was successfully called! ##########")
    return f"Tested: {value}"

# Log a message if the file loads and registers successfully
logger.info("########## Successfully loaded template_extras.py ##########")

# Keep your get_item filter here too, just in case the issue was subtle
@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Allows safely accessing dictionary items using variable keys in templates.
    Usage: {{ my_dictionary|get_item:key_variable }}
    Returns None if the key doesn't exist or the input is not a dictionary-like object.
    """
    if hasattr(dictionary, 'get'):
        return dictionary.get(key)
    return None