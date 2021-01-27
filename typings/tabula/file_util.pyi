"""
This type stub file was generated by pyright.
"""

from urllib.parse import uses_netloc, uses_params, uses_relative

_VALID_URLS = set(uses_relative + uses_netloc + uses_params)
MAX_FILE_SIZE = 200
def localize_file(path_or_buffer, user_agent=..., suffix=...):
    """Ensure localize target file.

    If the target file is remote, this function fetches into local storage.

    Args:
        path_or_buffer (str):
            File path or file like object or URL of target file.
        user_agent (str, optional):
            Set a custom user-agent when download a pdf from a url. Otherwise
            it uses the default ``urllib.request`` user-agent.
        suffix (str, optional):
            File extension to check.

    Returns:
        (str, bool):
            tuple of str and bool, which represents file name in local storage
            and temporary file flag.
    """
    ...

def is_file_like(obj):
    """Check file like object

    Args:
        obj:
            file like object.

    Returns:
        bool: file like object or not
    """
    ...

