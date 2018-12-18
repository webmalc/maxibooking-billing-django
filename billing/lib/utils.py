from importlib import import_module


def clsfstr(module, name):
    """
    Make class instance from string
    """
    return getattr(import_module(module), name)


def get_code(code_string):
    """
    Get user code and discount code from the code string
    """
    parts = code_string.split('~')
    if len(parts) > 2:
        raise ValueError('The code string contains more than one ~ character')
    if len(parts) == 1:
        parts.append(None)
    return parts
